import datetime as dt
import uuid

import fastapi as fa
import pydantic as pd
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import errors

from core.enums import LikeValueEnum
from core.shared import custom_dumps
from db.schemas.comment_likes import CommentLikesCreateSerializer, LikeCreateSerializer, CommentLikesReadSerializer, \
    LikeReadSerializer, CommentLikesUpdateSerializer
from db.schemas.film_comments import (
    FilmCommentsReadSerializer,
    FilmCommentReadSerializer,
    FilmCommentUpdateSerializer,
    FilmCommentCreateSerializer,
)
from services.cache.cache import RedisCache


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
                                   detail=f'cant find film {film_uuid=:}')
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
            session.abort_transaction()
            session.end_session()
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                                   detail=f'cant create comment to {film_uuid=:}: {e}')

    async def film_comments_get(self, comment_uuid: pd.UUID4) -> FilmCommentReadSerializer | None:
        res = await self.db.film_comments.find_one(
            {"film_comments": {"$elemMatch": {"comment_uuid": str(comment_uuid)}}},
            {"film_comments.$": 1})
        if res and 'film_comments' in res:
            return FilmCommentReadSerializer(**res["film_comments"][0])
        else:
            raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                   detail=f'cant find comment by {comment_uuid=:}')

    async def film_comments_update(self, comment_uuid: pd.UUID4,
                                   comment_ser: FilmCommentUpdateSerializer) -> FilmCommentReadSerializer | None:
        res = await self.db.film_comments.update_one(
            {"film_comments.comment_uuid": str(comment_uuid)},
            {"$set": {"film_comments.$.comment": comment_ser.comment, "film_comments.$.updated_at": dt.datetime.now()}},
        )

        if res.modified_count > 0:
            return await self.film_comments_get(comment_uuid)
        raise fa.HTTPException(status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
                               detail=f'cant update comment by {comment_uuid=:}')

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
                        return {'message': 'ok'}
                    else:
                        raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                               detail=f'cant find comment by {comment_uuid=:}')

            except errors.PyMongoError as e:
                await session.abort_transaction()
                raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                                       detail=f'cant delete comment by {comment_uuid=:}: {e}')

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

    async def comment_likes_list(self, comment_uuid: pd.UUID4) -> CommentLikesReadSerializer | None:
        res = await self.db.comment_likes.find_one({'comment_uuid': str(comment_uuid)})
        if res:
            return CommentLikesReadSerializer(**res)
        else:
            return None

    async def comment_likes_update(self, comment_uuid: pd.UUID4, comment_likes_ser: CommentLikesUpdateSerializer):
        res = await self.db.comment_likes.update_one(
            {"comment_uuid": str(comment_uuid)},
            {"$set": custom_dumps(comment_likes_ser)}
        )
        if res.modified_count > 0:
            return await self.comment_likes_list(comment_uuid)
        raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                               detail=f"can't create/update like/dislike for {comment_uuid=:}")

    async def comment_like_create(self, comment_uuid: pd.UUID4, user_uuid: pd.UUID4, like_ser: LikeCreateSerializer):
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

        if my_like.like_value == LikeValueEnum.like:
            comment_likes.likes_sum = comment_likes.likes_sum - 1
        elif my_like.like_value == LikeValueEnum.dislike:
            comment_likes.likes_sum = comment_likes.likes_sum + 1

        for ind, like in enumerate(comment_likes.likes):
            if str(like.user_uuid) == user_uuid:
                comment_likes.likes.pop(ind)

        return await self.comment_likes_update(comment_uuid, CommentLikesUpdateSerializer(**comment_likes.model_dump()))
