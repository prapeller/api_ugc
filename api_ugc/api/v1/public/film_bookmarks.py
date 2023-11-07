import fastapi as fa
import pydantic as pd

from core.dependencies import mongo_repo_dependency
from db.schemas.film_bookmarks import UserBookmarksSerializer
from services.mongo.mongo_repository import MongoRepository

router = fa.APIRouter()


@router.get('/{user_uuid}',
            response_model=UserBookmarksSerializer)
async def film_bookmarks_list_by_user(
        user_uuid: pd.UUID4,
        mongo_repo: MongoRepository = fa.Depends(mongo_repo_dependency),
):
    """list film_bookmarks of user"""
    return await mongo_repo.bookmarks_list_by_user(user_uuid)
