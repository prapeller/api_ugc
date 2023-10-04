import fastapi as fa
import pydantic as pd

from core.dependencies import mongo_repo_dependency, current_user_uuid_dependency
from db.schemas.comment_likes import CommentLikesReadSerializer, LikeCreateSerializer, LikeReadSerializer
from services.mongo.mongo_repository import MongoRepository

router = fa.APIRouter()


@router.get('/{comment_uuid}/my',
            response_model=LikeReadSerializer | None)
async def comment_likes_get_my(
        comment_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """get like of current user to particular comment"""
    return await mongo_repo.comment_like_get_by_user_uuid(comment_uuid, user_uuid)


@router.get('/{comment_uuid}',
            response_model=CommentLikesReadSerializer)
async def comment_likes_list(
        comment_uuid: pd.UUID4,
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """list likes to particular comment"""
    return await mongo_repo.comment_likes_list(comment_uuid)


@router.put('/{comment_uuid}',
            response_model=CommentLikesReadSerializer)
async def comment_likes_create_update(
        like_ser: LikeCreateSerializer,
        comment_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """create like by current_user to particular comment
            - if it doesn't exist
        update like:
            - if exists 'like'/'dislike', but sending other ('dislike'/'like')
        raise 400:
        - if exists 'like'/'dislike', and sending the same
    """
    return await mongo_repo.comment_like_update(comment_uuid, user_uuid, like_ser)


@router.delete('/{comment_uuid}')
async def comment_likes_delete(
        comment_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """delete like of current user to particular comment"""
    return await mongo_repo.comment_like_delete(comment_uuid, user_uuid)
