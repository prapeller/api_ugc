from contextlib import asynccontextmanager

import fastapi as fa
import uvicorn
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

import core.dependencies
from api.v1.auth.comment_likes import router as comment_likes_router
from api.v1.auth.film_bookmarks import router as film_bookmarks_router
from api.v1.auth.film_comments import router as film_comments_router
from api.v1.auth.film_ratings import router as film_ratings_router
from api.v1.auth.user_film_progress import router as user_film_progress_router
from api.v1.public.film_bookmarks import router as film_bookmarks_router_public
from core.config import settings
from core.logger_config import setup_logger

SERVICE_DIR = Path(__file__).resolve().parent
SERVICE_NAME = SERVICE_DIR.stem

logger = setup_logger(SERVICE_NAME, SERVICE_DIR)


@asynccontextmanager
async def lifespan(app: fa.FastAPI):
    # startup
    core.dependencies.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    yield
    # shutdown
    await core.dependencies.redis.close()


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = fa.FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url=f'/{settings.DOCS_URL}',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.middleware('http')
async def log_request_id(request: fa.Request, call_next):
    logger.info('Request processed', extra={'request_id': request.headers.get('X-Request-Id', 'None')})
    return await call_next(request)


v1_router_auth = fa.APIRouter()
v1_router_auth.include_router(user_film_progress_router, prefix='/user-film-progress', tags=['user_film_progress'])
v1_router_auth.include_router(film_comments_router, prefix='/film-comments', tags=['film_comments'])
v1_router_auth.include_router(film_ratings_router, prefix='/film-ratings', tags=['film_ratings'])
v1_router_auth.include_router(film_bookmarks_router, prefix='/film-bookmarks', tags=['film_bookmarks'])
v1_router_auth.include_router(comment_likes_router, prefix='/comment-likes', tags=['comment_likes'])

v1_router_public = fa.APIRouter()
v1_router_public.include_router(film_bookmarks_router_public, prefix='/film-bookmarks', tags=['film_bookmarks'])

app.include_router(v1_router_auth, prefix="/api/v1")
app.include_router(v1_router_public, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run('main:app', host=settings.API_UGC_HOST, port=settings.API_UGC_PORT, reload=True)
