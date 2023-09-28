import os
from pathlib import Path

import pydantic_settings as ps

BASE_DIR = Path(__file__).resolve().parent


class Settings(ps.BaseSettings):
    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int
    CLICKHOUSE_DB: str
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str

    USER_FILM_PROGRESS_TABLE: str

    KAFKA_ADVERTISED_LISTENERS: str

    class Config:
        extra = 'allow'

    def __init__(self, DOCKER, DEBUG):

        if DEBUG and DOCKER:
            super().__init__(_env_file=[
                BASE_DIR / '../.envs/.docker-compose-local/.clickhouse',
                BASE_DIR / '../.envs/.docker-compose-local/.kafka/.broker',
            ])
        elif DEBUG and not DOCKER:
            super().__init__(_env_file=[
                BASE_DIR / '../.envs/.local/.clickhouse',
                BASE_DIR / '../.envs/.local/.kafka/.broker',
            ])
        else:
            super().__init__(_env_file=[
                BASE_DIR / '../.envs/.prod/.clickhouse',
                BASE_DIR / '../.envs/.prod/.kafka/.broker',
            ])


DEBUG = os.getenv('DEBUG', False) == 'True'
DOCKER = os.getenv('DOCKER', False) == 'True'

settings = Settings(DOCKER, DEBUG)

KAFKA_USER_FILM_PROGRESS_TOPIC_NAME = 'user_film_progress'
KAFKA_BROKER_PLAINTEXT_HOST_PORT = settings.KAFKA_ADVERTISED_LISTENERS.split(',')[1].replace('PLAINTEXT_HOST://', '')
