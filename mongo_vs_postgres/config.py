import os
from pathlib import Path

import pydantic_settings as pd_settings

BASE_DIR = Path(__file__).resolve().parent.parent


class PostgresSettings(pd_settings.BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    class Config:
        extra = 'allow'

    def __init__(self, DOCKER, DEBUG):
        if DEBUG and DOCKER:
            super().__init__(_env_file=[BASE_DIR / '.envs/.docker-compose-local/.postgres'])
        else: # DEBUG and not DOCKER
            super().__init__(_env_file=[BASE_DIR / '.envs/.local/.postgres'])



class MongoSettings(pd_settings.BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str
    MONGO_USER: str
    MONGO_PASSWORD: str

    class Config:
        extra = 'allow'

    def __init__(self, DOCKER, DEBUG):
        if DEBUG and DOCKER:
            super().__init__(_env_file=[BASE_DIR / '.envs/.docker-compose-local/.mongo'])
        else: # DEBUG and not DOCKER
            super().__init__(_env_file=[BASE_DIR / '.envs/.local/.mongo'])


DOCKER = os.getenv('DOCKER')
DEBUG = os.getenv('DEBUG')

postgres_settings = PostgresSettings(DOCKER, DEBUG)
mongo_settings = MongoSettings(DOCKER, DEBUG)
