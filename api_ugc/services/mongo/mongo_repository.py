import datetime as dt
import uuid

import fastapi as fa
import pydantic as pd
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import errors

from core.enums import LikeValueEnum
from core.shared import custom_dumps
from db.schemas.comment_likes import (
    CommentLikesCreateSerializer,
    LikeCreateSerializer,
    CommentLikesReadSerializer,
    LikeReadSerializer,
    CommentLikesUpdateSerializer,
)
from db.schemas.film_bookmarks import UserBookmarksSerializer, BookmarkSerializer
from db.schemas.film_comments import (
    FilmCommentsReadSerializer,
    FilmCommentReadSerializer,
    FilmCommentUpdateSerializer,
    FilmCommentCreateSerializer,
)
from db.schemas.film_ratings import (
    FilmRatingsReadSerializer,
    FilmRatingReadSerializer,
    UserRatingUpdateSerializer,
    UserRatingReadSerializer,
)
from services.cache.cache import RedisCache
from services.mongo.logger_config import logger


class MongoRepository():
    def __init__(self, conn_string, db_name, cache):
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(conn_string)
        self.db = self.client[db_name]
        self.cache: RedisCache = cache

    def close_connection(self):
        self.client.close()

    async def film_comments_list(self, film_uuid: pd.UUID4, limit: int, offset: int):
        try:
            res = await self.cache.get(f'film_comments_by_{film_uuid=:}_{limit=:}_{offset=:}')
            if res is None:
                res = await self.db.film_comments.find_one({'film_uuid': str(film_uuid)})
                res['film_comments'] = res.get('film_comments')[offset:offset + limit]
                await self.cache.set(f'film_comments_by_{film_uuid=:}_{limit=:}_{offset=:}', res)
        except IndexError:
            raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                   detail=f'film not found, {film_uuid=:}')
        film_comments = FilmCommentsReadSerializer(film_uuid=film_uuid, film_comments=res.get('film_comments'))
        return film_comments

    async def film_comments_create(self, film_uuid: pd.UUID4, user_uuid: pd.UUID4,
                                   comment_ser: FilmCommentCreateSerializer) -> FilmCommentReadSerializer | None:
        comment_uuid = uuid.uuid4()
        comment_ser.comment_uuid = comment_uuid
        comment_ser.user_uuid = user_uuid
        comment_ser.created_at = dt.datetime.now()
        session = await self.client.start_session()
        try:
            async with session.start_transaction():
                res1 = await self.db.film_comments.update_one(
                    {"film_uuid": str(film_uuid)},
                    {"$push": {"film_comments": custom_dumps(comment_ser)}}
                )
                if res1.modified_count > 0:
                    await self.db.comment_likes.insert_one(
                        custom_dumps(CommentLikesCreateSerializer(comment_uuid=comment_uuid)))
                    session.commit_transaction()
                    session.end_session()
                    return await self.film_comments_get(comment_uuid)
        except errors.PyMongoError as e:
            detail = f"can't create comment to {film_uuid=:}, {user_uuid=:}: {e}"
            logger.error(detail)
            session.abort_transaction()
            session.end_session()
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                                   detail=detail)

    async def film_comments_get(self, comment_uuid: pd.UUID4) -> FilmCommentReadSerializer | None:
        res = await self.db.film_comments.find_one(
            {"film_comments": {"$elemMatch": {"comment_uuid": str(comment_uuid)}}},
            {"film_comments.$": 1})
        if res and 'film_comments' in res:
            return FilmCommentReadSerializer(**res["film_comments"][0])
        else:
            raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                   detail=f'comment not found, {comment_uuid=:}')

    async def film_comments_update(self, comment_uuid: pd.UUID4,
                                   comment_ser: FilmCommentUpdateSerializer) -> FilmCommentReadSerializer | None:
        res = await self.db.film_comments.update_one(
            {"film_comments.comment_uuid": str(comment_uuid)},
            {"$set": {"film_comments.$.comment": comment_ser.comment, "film_comments.$.updated_at": dt.datetime.now()}},
        )

        if res.modified_count > 0:
            return await self.film_comments_get(comment_uuid)
        raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                               detail=f"can't update comment by {comment_uuid=:}")

    async def film_comments_delete(self, comment_uuid: pd.UUID4):
        async with await self.client.start_session() as session:
            try:
                async with session.start_transaction():
                    res = await self.db.film_comments.update_one(
                        {'film_comments.comment_uuid': str(comment_uuid)},
                        {"$pull": {"film_comments": {"comment_uuid": str(comment_uuid)}}}
                    )
                    if res.modified_count > 0:
                        await self.db.comment_likes.delete_one({"comment_uuid": str(comment_uuid)})
                        await session.commit_transaction()
                        return {'detail': 'ok'}
                    else:
                        raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                               detail=f'comment not found, {comment_uuid=:}')

            except errors.PyMongoError as e:
                detail = f"can't delete comment by {comment_uuid=:}: {e}"
                logger.error(detail)
                await session.abort_transaction()
                raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                                       detail=detail)

    async def comment_like_get_by_user_uuid(self, comment_uuid: pd.UUID4,
                                            user_uuid: pd.UUID4) -> LikeReadSerializer | None:
        res = await self.db.comment_likes.find_one(
            {'comment_uuid': str(comment_uuid), 'likes': {'$elemMatch': {'user_uuid': str(user_uuid)}}},
            {'likes.$': 1}
        )
        if res and 'likes' in res:
            return LikeReadSerializer(**res["likes"][0])
        else:
            return None

    async def comment_likes_list(self, comment_uuid: pd.UUID4) -> CommentLikesReadSerializer:
        res = await self.db.comment_likes.find_one({'comment_uuid': str(comment_uuid)})
        if res:
            return CommentLikesReadSerializer(**res)
        else:
            raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                   detail=f"comment_likes not found, {comment_uuid=:}")

    async def comment_likes_update(self, comment_uuid: pd.UUID4, comment_likes_ser: CommentLikesUpdateSerializer):
        res = await self.db.comment_likes.update_one(
            {"comment_uuid": str(comment_uuid)},
            {"$set": custom_dumps(comment_likes_ser)}
        )
        if res.modified_count > 0:
            return await self.comment_likes_list(comment_uuid)

        else:
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                                   detail=f"can't update comment_likes, {comment_uuid=:}")

    async def comment_like_update(self, comment_uuid: pd.UUID4, user_uuid: pd.UUID4, like_ser: LikeCreateSerializer):
        """
        A) if current_user's like doesn't exist
          - update likes_sum (add like_value to)
          - add like to comment_likes.likes
        B) elif current_user's like exists
          - update likes_sum (if prev was 'like' and new is 'dislike' => -2, if prev was 'dislike' and new is 'like' => +2)
          - replace my_like in comment_likes.likes
        C) update db.comment_likes
          """

        comment_likes = await self.comment_likes_list(comment_uuid)
        my_like = await self.comment_like_get_by_user_uuid(comment_uuid, user_uuid)
        like_ser.user_uuid = user_uuid

        # A) if current_user's like doesn't exist
        if my_like is None:
            comment_likes.likes_sum = comment_likes.likes_sum + like_ser.like_value
            comment_likes.likes.append(like_ser)

        # B) elif current_user's like exists
        else:
            if my_like.like_value == LikeValueEnum.like and like_ser.like_value == LikeValueEnum.dislike:
                comment_likes.likes_sum = comment_likes.likes_sum - 2
            elif my_like.like_value == LikeValueEnum.dislike and like_ser.like_value == LikeValueEnum.like:
                comment_likes.likes_sum = comment_likes.likes_sum + 2

            for ind, like in enumerate(comment_likes.likes):
                if str(like.user_uuid) == user_uuid:
                    comment_likes.likes[ind] = like_ser
                    break

        # C) update comment_likes
        return await self.comment_likes_update(comment_uuid, CommentLikesUpdateSerializer(**comment_likes.model_dump()))

    async def comment_like_delete(self, comment_uuid: pd.UUID4, user_uuid: pd.UUID4):
        comment_likes = await self.comment_likes_list(comment_uuid)
        my_like = await self.comment_like_get_by_user_uuid(comment_uuid, user_uuid)
        if my_like is None:
            raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                   detail=f"current_users's like not found, {comment_uuid=:}")

        if my_like.like_value == LikeValueEnum.like:
            comment_likes.likes_sum = comment_likes.likes_sum - 1
        elif my_like.like_value == LikeValueEnum.dislike:
            comment_likes.likes_sum = comment_likes.likes_sum + 1

        for ind, like in enumerate(comment_likes.likes):
            if str(like.user_uuid) == user_uuid:
                comment_likes.likes.pop(ind)

        await self.comment_likes_update(comment_uuid, CommentLikesUpdateSerializer(**comment_likes.model_dump()))
        return {'detail': 'ok'}

    async def ratings_list_by_user(self, user_uuid: pd.UUID4) -> list[FilmRatingReadSerializer]:
        try:
            res = await self.db.user_ratings_bookmarks.find_one({'user_uuid': str(user_uuid)})
            if res is None:
                raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                       detail=f'film_ratings not found, {user_uuid=:}')
            return res.get('film_ratings', [])
        except errors.PyMongoError as e:
            detail = f"can't get 'film_ratings' for {user_uuid=:}: {e}"
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                                   detail=detail)

    async def ratings_list_by_film(self, film_uuid: pd.UUID4) -> FilmRatingsReadSerializer:
        try:
            res = await self.cache.get(f'film_ratings_{film_uuid=:}')
            if res is None:
                res = await self.db.film_ratings.find_one({'film_uuid': str(film_uuid)})
                await self.cache.set(f'film_ratings_{film_uuid=:}', res)

            return FilmRatingsReadSerializer(film_uuid=film_uuid, avg_rating=res.get('avg_rating'),
                                             user_ratings=res.get('user_ratings'))

        except errors.PyMongoError as e:
            detail = f"can't list film_ratings, {film_uuid=:}: {e}"
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)

    async def rating_get_by_film_by_user(self, film_uuid: pd.UUID4, user_uuid: pd.UUID4) -> FilmRatingReadSerializer:
        try:
            user_ratings_bookmarks_res = await self.db.user_ratings_bookmarks.find_one({'user_uuid': user_uuid})

            if user_ratings_bookmarks_res:
                user_ratings = user_ratings_bookmarks_res.get('film_ratings')
                for r in user_ratings:
                    if r['film_uuid'] == str(film_uuid):
                        return FilmRatingReadSerializer(**r)
            else:
                raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                       detail=f'film_rating not found, {user_uuid=:}, {film_uuid=:}')

        except errors.PyMongoError as e:
            detail = f"can't get user rating, {user_uuid=:} {film_uuid=:}: {e}"
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)

    async def rating_update_by_film_by_user(self, film_uuid: pd.UUID4, user_uuid: pd.UUID4,
                                            rating_ser: UserRatingUpdateSerializer) -> UserRatingReadSerializer:
        session = await self.client.start_session()
        try:
            async with session.start_transaction():
                # Update the user's rating in the user_ratings_bookmarks collection
                user_ratings_bookmarks_res = await self.db.user_ratings_bookmarks.update_one(
                    {'user_uuid': str(user_uuid), 'film_ratings.film_uuid': str(film_uuid)},
                    {'$set': {'film_ratings.$.rating': rating_ser.rating}}
                )
                if user_ratings_bookmarks_res.modified_count == 0:
                    detail = f"can't update current_user rating, {user_uuid=:}, {film_uuid=:}"
                    raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)

                # Update the film's average rating in the film_ratings collection
                film_ratings_res = await self.db.film_ratings.find_one({'film_uuid': str(film_uuid)})
                old_user_ratings = film_ratings_res.get('user_ratings', []) if film_ratings_res else []

                # Replace or add the new rating for the specific user
                new_user_ratings = [
                    r if r['user_uuid'] != str(user_uuid) else {'user_uuid': str(user_uuid),
                                                                'rating': rating_ser.rating}
                    for r in old_user_ratings
                ]
                if all(r['user_uuid'] != str(user_uuid) for r in old_user_ratings):
                    new_user_ratings.append({'user_uuid': str(user_uuid), 'rating': rating_ser.rating})

                # Calculate the new average rating
                new_avg = sum(r['rating'] for r in new_user_ratings) / len(new_user_ratings) if new_user_ratings else 0

                # Update film_ratings with the new average and user ratings
                await self.db.film_ratings.update_one(
                    {'film_uuid': str(film_uuid)},
                    {'$set': {'avg_rating': new_avg, 'user_ratings': new_user_ratings}},
                    upsert=True
                )
                session.commit_transaction()
                return UserRatingReadSerializer(user_uuid=user_uuid, rating=rating_ser.rating)
        except errors.PyMongoError as e:
            detail = f"can't update user rating, {film_uuid=:}: {e}"
            logger.error(detail)
            session.abort_transaction()
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)
        finally:
            session.end_session()

    async def ratings_delete_by_film_by_user(self, film_uuid: pd.UUID4, user_uuid: pd.UUID4):
        session = await self.client.start_session()
        try:
            async with session.start_transaction():
                # Remove the user's rating from the user_ratings_bookmarks collection
                user_ratings_bookmarks_res = await self.db.user_ratings_bookmarks.update_one(
                    {'user_uuid': str(user_uuid)},
                    {'$pull': {'film_ratings': {'film_uuid': str(film_uuid)}}}
                )
                if user_ratings_bookmarks_res.modified_count == 0:
                    detail = f"can't delete current_user rating, {user_uuid=:}, {film_uuid=:}"
                    raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)

                # Update the film's average rating in the film_ratings collection
                film_ratings_res = await self.db.film_ratings.find_one({'film_uuid': str(film_uuid)})
                old_user_ratings = film_ratings_res.get('user_ratings', []) if film_ratings_res else []

                # Remove the user's rating from the list
                new_user_ratings = [r for r in old_user_ratings if r['user_uuid'] != str(user_uuid)]

                # Calculate the new average rating
                if len(new_user_ratings) > 0:
                    new_avg = sum(r['rating'] for r in new_user_ratings) / len(new_user_ratings)
                else:
                    new_avg = 0.0

                # Update the film_ratings collection
                await self.db.film_ratings.update_one(
                    {'film_uuid': str(film_uuid)},
                    {'$set': {'avg_rating': new_avg, 'user_ratings': new_user_ratings}}
                )

                await session.commit_transaction()
                return {'detail': 'ok'}

        except errors.PyMongoError as e:
            detail = f"can't delete current_user rating, {user_uuid=:}, {film_uuid=:}: {e}"
            logger.error(detail)
            await session.abort_transaction()
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)

    async def bookmarks_list_by_user(self, user_uuid) -> UserBookmarksSerializer:
        try:
            res = await self.db.user_ratings_bookmarks.find_one({'user_uuid': str(user_uuid)})
            if res is None:
                raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                       detail=f'film_bookmarks not found, {user_uuid=:}')
            film_bookmarks = res.get('film_bookmarks', [])
            return UserBookmarksSerializer(user_uuid=user_uuid, film_bookmarks=film_bookmarks)

        except errors.PyMongoError as e:
            detail = f"can't list film_bookmarks, {user_uuid=:}: {e}"
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)

    async def bookmarks_create_by_user(self, user_uuid, bookmark_ser) -> BookmarkSerializer:
        try:
            my_user_bookmarks: UserBookmarksSerializer = await self.bookmarks_list_by_user(user_uuid)
            if any([b.film_uuid == bookmark_ser.film_uuid for b in my_user_bookmarks.film_bookmarks]):
                detail = f"film_bookmark, {user_uuid=:}, {bookmark_ser=:} already exists"
                raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                                       detail=detail)

            res = await self.db.user_ratings_bookmarks.update_one(
                {'user_uuid': str(user_uuid)},
                {"$push": {"film_bookmarks": custom_dumps(bookmark_ser)}})
            if res.modified_count > 0:
                return bookmark_ser

        except errors.PyMongoError as e:
            detail = f"can't create film_bookmark, {user_uuid=:}, {bookmark_ser}: {e}"
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)

    async def bookmarks_delete_by_film_by_user(self, film_uuid, user_uuid):
        try:
            result = await self.db.user_ratings_bookmarks.update_one(
                {'user_uuid': str(user_uuid)},
                {'$pull': {'film_bookmarks': {'film_uuid': str(film_uuid)}}}
            )
            if result.modified_count > 0:
                return {'detail': 'ok'}
            else:
                detail = f"can't delete film_bookmark, {user_uuid=:}, {film_uuid=:}"
                raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)
        except errors.PyMongoError as e:
            detail = f"can't delete film_bookmark, {user_uuid=:}, {film_uuid=:}: {e}"
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST, detail=detail)
