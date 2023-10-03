import fastapi as fa
import pydantic as pd

from core.dependencies import mongo_repo_dependency, current_user_uuid_dependency
from db.schemas.comment_likes import CommentLikesReadSerializer, LikeCreateSerializer, LikeReadSerializer
from services.mongo.mongo_repository import MongoRepository

router = fa.APIRouter()


@router.get('/my',
            response_model=LikeReadSerializer | None)
async def comment_likes_get_my(
        comment_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """get like of current user to particular comment"""
    return await mongo_repo.comment_like_get_by_user_uuid(comment_uuid, user_uuid)


@router.get('/',
            response_model=CommentLikesReadSerializer | None)
async def comment_likes_list(
        comment_uuid: pd.UUID4,
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """list likes to particular comment"""
    return await mongo_repo.comment_likes_list(comment_uuid)


@router.post('/',
             response_model=CommentLikesReadSerializer)
async def comment_likes_create(
        like_ser: LikeCreateSerializer,
        comment_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """create like by current_user to particular comment
        - if exists 'like', but is going to create 'dislike' - change it
        - if exists 'dislike', but is going to create 'like' - change it
        - if exists 'like', and going to create 'like' - do nothing
        - if exists 'dislike', and going to create 'dislike' - do nothing
    """
    return await mongo_repo.comment_like_create(comment_uuid, user_uuid, like_ser)


@router.delete('/')
async def comment_likes_delete(
        comment_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """delete like of current user"""
    return await mongo_repo.comment_like_delete(comment_uuid, user_uuid)
