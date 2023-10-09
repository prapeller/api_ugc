import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from tests.conftest import test_settings


@pytest_asyncio.fixture
async def film_uuid():
    client = AsyncIOMotorClient(f'mongodb://{test_settings.MONGO_HOST}:{test_settings.MONGO_PORT}')
    db = client[test_settings.MONGO_DB]
    document = await db.user_ratings_bookmarks.find_one({}, {'film_bookmarks': 1})
    film_uuid = document['film_bookmarks'][0]['film_uuid'] if document and 'film_bookmarks' in document else None
    client.close()
    return film_uuid


@pytest_asyncio.fixture
async def comment_uuid():
    client = AsyncIOMotorClient(f'mongodb://{test_settings.MONGO_HOST}:{test_settings.MONGO_PORT}')
    db = client[test_settings.MONGO_DB]
    document = await db.film_comments.find_one({}, {'film_comments': 1})
    comment_uuid = document['film_comments'][0]['comment_uuid'] if document and 'film_comments' in document else None
    client.close()
    return comment_uuid
