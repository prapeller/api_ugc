import os
from pathlib import Path

import pydantic as pd
import pydantic_settings as ps


class Settings(ps.BaseSettings):
    PROJECT_NAME: str
    DOCS_URL: str

    API_UGC_HOST: str
    API_UGC_PORT: int

    API_AUTH_HOST: str
    API_AUTH_PORT: int
    SENTRY_DSN: pd.HttpUrl

    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int
    CLICKHOUSE_USER: str
    CLICKHOUSE_DB: str
    CLICKHOUSE_PASSWORD: str
    USER_FILM_PROGRESS_TABLE: str

    KAFKA_ADVERTISED_LISTENERS: str

    REDIS_HOST: str
    REDIS_PORT: int

    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str
    MONGO_USER: str
    MONGO_PASSWORD: str

    LOGSTASH_HOST: str
    LOGSTASH_PORT: int

    class Config:
        extra = 'allow'

    def __init__(self, DOCKER, DEBUG, BASE_DIR):

        if DEBUG and DOCKER:
            super().__init__(_env_file=[BASE_DIR / '.envs/.docker-compose-local/.api',
                                        BASE_DIR / '.envs/.docker-compose-local/.elk/.logstash',
                                        BASE_DIR / '.envs/.docker-compose-local/.clickhouse',
                                        BASE_DIR / '.envs/.docker-compose-local/.mongo',
                                        BASE_DIR / '.envs/.docker-compose-local/.kafka/.broker',
                                        BASE_DIR / '.envs/.docker-compose-local/.redis'])
        elif DEBUG and not DOCKER:
            super().__init__(_env_file=[BASE_DIR / '.envs/.local/.api',
                                        BASE_DIR / '.envs/.local/.elk/.logstash',
                                        BASE_DIR / '.envs/.local/.clickhouse',
                                        BASE_DIR / '.envs/.local/.mongo',
                                        BASE_DIR / '.envs/.local/.kafka/.broker',
                                        BASE_DIR / '.envs/.local/.redis'])
        else:
            super().__init__(_env_file=[BASE_DIR / '.envs/.prod/.api',
                                        BASE_DIR / '.envs/.prod/.elk/.logstash',
                                        BASE_DIR / '.envs/.prod/.clickhouse',
                                        BASE_DIR / '.envs/.prod/.mongo',
                                        BASE_DIR / '.envs/.prod/.kafka/.broker',
                                        BASE_DIR / '.envs/.prod/.redis'])


DEBUG = os.getenv('DEBUG', False) == 'True'
DOCKER = os.getenv('DOCKER', False) == 'True'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

settings = Settings(DOCKER, DEBUG, BASE_DIR)

KAFKA_USER_FILM_PROGRESS_TOPIC_NAME = 'user_film_progress'
KAFKA_BROKER_PLAINTEXT_HOST_PORT = settings.KAFKA_ADVERTISED_LISTENERS.split(',')[1].replace('PLAINTEXT_HOST://', '')
REDIS_CACHE_EXPIRES_IN_SECONDS = 30
