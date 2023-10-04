import fastapi as fa
import pydantic as pd

from core.dependencies import mongo_repo_dependency, current_user_uuid_dependency
from db.schemas.film_ratings import FilmRatingReadSerializer, FilmRatingsReadSerializer, UserRatingUpdateSerializer, \
    UserRatingReadSerializer
from services.mongo.mongo_repository import MongoRepository

router = fa.APIRouter()


@router.get('/my',
            response_model=list[FilmRatingReadSerializer])
async def film_ratings_list_my(
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """list ratings of current user to all films"""
    return await mongo_repo.ratings_list_by_user(user_uuid)


@router.get('/{film_uuid}/my',
            response_model=FilmRatingReadSerializer)
async def film_ratings_get_by_film_my(
        film_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """get rating of current user to particular film"""
    return await mongo_repo.rating_get_by_film_by_user(film_uuid, user_uuid)


@router.get('/{film_uuid}',
            response_model=FilmRatingsReadSerializer)
async def film_ratings_list_by_film(
        film_uuid: pd.UUID4,
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency)
):
    """list all ratings and average_rating of particular film"""
    return await mongo_repo.ratings_list_by_film(film_uuid)


@router.put('/{film_uuid}',
            response_model=UserRatingReadSerializer)
async def film_ratings_update_my(
        film_uuid: pd.UUID4,
        rating_ser: UserRatingUpdateSerializer,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency)
):
    """update rating of current user to particular film if it exists (create if it doesn't exist)
    (in user_ratings_bookmarks and in film_ratings with recalculating avg_rating)"""
    return await mongo_repo.rating_update_by_film_by_user(film_uuid, user_uuid, rating_ser)


@router.delete('/{film_uuid}')
async def film_comments_delete_my(
        film_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency)
):
    """delete rating of current user to particular film if it exists"""
    return await mongo_repo.ratings_delete_by_film_by_user(film_uuid, user_uuid)
