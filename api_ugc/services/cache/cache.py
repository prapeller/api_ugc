from abc import ABC, abstractmethod
from pathlib import Path

import orjson
from redis.asyncio import Redis
from redis.exceptions import RedisError

from core import config
from core.logger_config import setup_logger
from core.shared import custom_dumps

SERVICE_DIR = Path(__file__).resolve().parent
SERVICE_NAME = SERVICE_DIR.stem

logger = setup_logger(SERVICE_NAME, SERVICE_DIR)


class Cache(ABC):

    @abstractmethod
    def set(self, cache_key, data):
        pass

    @abstractmethod
    def get(self, cache_key):
        pass


class RedisCache(Cache):

    def __init__(self, redis: Redis):
        self.redis: Redis = redis

    async def set(self, cache_key: str, data: dict):
        data: dict = custom_dumps(data)
        data: bytes = orjson.dumps(data)
        try:
            await self.redis.set(cache_key, data, config.REDIS_CACHE_EXPIRE_IN_SECONDS)
            logger.debug('set by {}, {}'.format(cache_key, data))
        except (TypeError, RedisError) as e:
            logger.error("can't set by {}, {}".format(cache_key, e))

    async def get(self, cache_key: str) -> dict | None:
        try:
            data: bytes = await self.redis.get(cache_key)
            if data is not None:
                data: dict = orjson.loads(data)
                logger.debug('get by {}, {} '.format(cache_key, data))
            return data
        except RedisError as e:
            logger.error("can't get by {}, {}".format(cache_key, e))
            return None
