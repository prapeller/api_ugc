import json
from typing import Generator

import clickhouse_driver
import fastapi as fa
import httpx
import pydantic as pd
from aiokafka import AIOKafkaProducer
from clickhouse_driver.dbapi.cursor import Cursor as CHCursor
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from kafka import KafkaProducer
from redis.asyncio import Redis

from core import config
from core.config import settings
from core.exceptions import UnauthorizedException
from services.cache.cache import RedisCache
from services.clickhouse.clickhouse_repository import CHRepository
from services.mongo.mongo_repository import MongoRepository

redis: Redis | None = None


async def redis_dependency() -> Redis:
    return redis


async def redis_cache_dependency(redis: Redis = Depends(redis_dependency)) -> RedisCache:
    return RedisCache(redis)


oauth2_scheme_local = OAuth2PasswordBearer(
    tokenUrl=f"http://{settings.API_AUTH_HOST}:{settings.API_AUTH_PORT}/api/v1/auth/login")


async def verified_access_token_dependency(
        request: fa.Request,
        access_token: str = fa.Depends(oauth2_scheme_local),
) -> dict:
    url = f"http://{settings.API_AUTH_HOST}:{settings.API_AUTH_PORT}/api/v1/auth/verify-access-token"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        'useragent': request.headers.get("user-agent"),
        # 'ip': '172.20.0.5',
        'ip': request.client.host,
        'access_token': access_token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
    if resp.status_code != fa.status.HTTP_200_OK:
        raise UnauthorizedException
    return json.loads(resp.text)


async def current_user_uuid_dependency(
        access_token: dict = fa.Depends(verified_access_token_dependency),
) -> pd.UUID4:
    # return pd.UUID4('0084ba96-8688-4a1b-b4a2-691c38a99e61')
    return pd.UUID4(access_token.get('sub'))


async def kafka_producer_dependency() -> Generator[KafkaProducer, None, None]:
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_BROKER_PLAINTEXT_HOST_PORT,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    try:
        yield producer
    finally:
        producer.close()


async def aiokafka_producer_dependency() -> Generator[AIOKafkaProducer, None, None]:
    producer = AIOKafkaProducer(
        bootstrap_servers=config.KAFKA_BROKER_PLAINTEXT_HOST_PORT,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    try:
        await producer.start()
        yield producer
    finally:
        await producer.stop()


async def clickhouse_cursor_dependency() -> Generator[CHCursor, None, None]:
    clickhouse_conn = clickhouse_driver.connect(host=settings.CLICKHOUSE_HOST,
                                                port=settings.CLICKHOUSE_PORT,
                                                user=settings.CLICKHOUSE_USER,
                                                password=settings.CLICKHOUSE_PASSWORD,
                                                database=settings.CLICKHOUSE_DB)
    cursor = clickhouse_conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        clickhouse_conn.close()


async def clickhouse_repo_dependency(
        cursor: CHCursor = fa.Depends(clickhouse_cursor_dependency),
) -> Generator[CHRepository, None, None]:
    repo = CHRepository(cursor)
    try:
        yield repo
    finally:
        repo.cursor.close()


async def mongo_repo_dependency(
        redis_cache: RedisCache = fa.Depends(redis_cache_dependency),
) -> Generator[MongoRepository, None, None]:
    repo = MongoRepository(
        conn_string=f'mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}',
        db_name=settings.MONGO_DB,
        cache=redis_cache)
    try:
        yield repo
    finally:
        repo.close_connection()


async def pagination_params_dependency(
        offset: int | None = 0,
        limit: int | None = 20,
) -> dict:
    return {
        'offset': offset,
        'limit': limit,
    }
