import json

import fastapi as fa
import httpx
from aiokafka import AIOKafkaProducer
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from kafka import KafkaProducer
from redis.asyncio import Redis

from core import config
from core.config import settings
from core.exceptions import UnauthorizedException
from services.cache import RedisCache

redis: Redis | None = None


async def redis_dependency() -> Redis:
    return redis


async def cache_dependency(
        redis: Redis = Depends(redis_dependency),
) -> RedisCache:
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
        # 'ip': request.client.host,
        'ip': '172.20.0.5',
        'access_token': access_token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
    if resp.status_code != fa.status.HTTP_200_OK:
        raise UnauthorizedException
    return json.loads(resp.text)


async def get_current_user_id_dependency(
        access_token: dict = fa.Depends(verified_access_token_dependency),
) -> str:
    return access_token.get('sub')


async def get_kafka_producer_dependency():
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_BROKER_PLAINTEXT_HOST_PORT,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    try:
        yield producer
    finally:
        producer.close()


async def get_aiokafka_producer_dependency():
    producer = AIOKafkaProducer(
        bootstrap_servers=config.KAFKA_BROKER_PLAINTEXT_HOST_PORT,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    try:
        await producer.start()
        yield producer
    finally:
        await producer.stop()
