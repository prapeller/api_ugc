import fastapi as fa
import pydantic as pd

from core.dependencies import mongo_repo_dependency, current_user_uuid_dependency
from db.schemas.film_bookmarks import UserBookmarksSerializer, BookmarkSerializer
from db.schemas.film_ratings import FilmRatingsReadSerializer, UserRatingUpdateSerializer, \
    UserRatingReadSerializer
from services.mongo.mongo_repository import MongoRepository

router = fa.APIRouter()


@router.get('/my',
            response_model=UserBookmarksSerializer)
async def film_bookmarks_list_my(
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """list film_bookmarks of current user"""
    return await mongo_repo.bookmarks_list_by_user(user_uuid)


@router.post('/',
            response_model=BookmarkSerializer)
async def film_bookmarks_create(
        bookmark_ser: BookmarkSerializer,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency)
):
    """create film_bookmarks of current user"""
    return await mongo_repo.bookmarks_create_by_user(user_uuid, bookmark_ser)


@router.delete('/{film_uuid}')
async def film_comments_delete(
        film_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency)
):
    return await mongo_repo.bookmarks_delete_by_film_by_user(film_uuid, user_uuid)
