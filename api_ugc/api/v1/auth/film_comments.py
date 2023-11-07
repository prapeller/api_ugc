import fastapi as fa
import pydantic as pd

from core.dependencies import mongo_repo_dependency, current_user_uuid_dependency, pagination_params_dependency
from db.schemas.film_comments import FilmCommentsReadSerializer, FilmCommentReadSerializer, FilmCommentUpdateSerializer, \
    FilmCommentCreateSerializer
from services.mongo.mongo_repository import MongoRepository

router = fa.APIRouter()


@router.get('/',
            response_model=FilmCommentsReadSerializer)
async def film_comments_list(
        film_uuid: pd.UUID4,
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
        pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """list film_comments for particular film by film_uuid"""
    return await mongo_repo.film_comments_list(film_uuid,
                                               limit=pagination_params.get('limit'),
                                               offset=pagination_params.get('offset'))


@router.get('/{comment_uuid}',
            response_model=FilmCommentReadSerializer)
async def film_comments_read(
        comment_uuid: pd.UUID4,
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """get film_comment by comment_uuid"""
    return await mongo_repo.film_comments_get(comment_uuid)


@router.put('/{comment_uuid}',
            response_model=FilmCommentReadSerializer)
async def film_comments_update(
        comment_uuid: pd.UUID4,
        comment_ser: FilmCommentUpdateSerializer,
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """update film_comment by comment_uuid"""
    return await mongo_repo.film_comments_update(comment_uuid, comment_ser)


@router.delete('/{comment_uuid}')
async def film_comments_delete(
        comment_uuid: pd.UUID4,
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """delete film_comment by comment_uuid"""
    return await mongo_repo.film_comments_delete(comment_uuid)


@router.post('/',
             response_model=FilmCommentReadSerializer)
async def film_comments_create(
        comment_ser: FilmCommentCreateSerializer,
        film_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """create film_comment of current_user to particular film"""
    comment_ser.user_uuid = user_uuid
    return await mongo_repo.film_comments_create(film_uuid, user_uuid, comment_ser)
