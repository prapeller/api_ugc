import fastapi as fa
import uvicorn
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

import core.dependencies
from api.v1.user_film_progress import router as user_film_progress_router
from api.v1.film_comments import router as film_coments_router
from api.v1.film_ratings import router as film_ratings_router
from api.v1.film_bookmarks import router as film_bookmarks_router
from api.v1.comment_likes import router as comment_likes_router
from core.config import settings

app = fa.FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=f'/{settings.DOCS_URL}',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    core.dependencies.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


@app.on_event('shutdown')
async def shutdown():
    await core.dependencies.redis.close()


v1_router_auth = fa.APIRouter()
v1_router_auth.include_router(user_film_progress_router, prefix='/user-film-progress', tags=['user_film_progress'])
v1_router_auth.include_router(film_coments_router, prefix='/film-comments', tags=['film_comments'])
v1_router_auth.include_router(film_ratings_router, prefix='/film-ratings', tags=['film_ratings'])
v1_router_auth.include_router(film_bookmarks_router, prefix='/film-bookmarks', tags=['film_bookmarks'])
v1_router_auth.include_router(comment_likes_router, prefix='/comment-likes', tags=['comment_likes'])

v1_router_public = fa.APIRouter()

app.include_router(v1_router_auth, prefix="/api/v1")
app.include_router(v1_router_public, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run('main:app', host=settings.API_UGC_HOST, port=settings.API_UGC_PORT, reload=True)
