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
        env_file = BASE_DIR / '.envs/.local/.postgres'
        extra = 'allow'


class MongoSettings(pd_settings.BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str
    MONGO_USER: str
    MONGO_PASSWORD: str

    class Config:
        env_file = BASE_DIR / '.envs/.local/.mongo'
        extra = 'allow'


postgres_settings = PostgresSettings()
mongo_settings = MongoSettings()
