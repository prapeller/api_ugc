import os
from pathlib import Path

os.environ['DEBUG'] = 'True'
os.environ['DOCKER'] = 'False'
from api_ugc.core.config import Settings

DEBUG = os.getenv('DEBUG', False) == 'True'
DOCKER = os.getenv('DOCKER', False) == 'True'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

test_settings = Settings(DOCKER, DEBUG, BASE_DIR)

pytest_plugins = (
    'tests.functional.plugins.aiohttp_plugin',
    'tests.functional.plugins.mongo_plugin',
    'tests.functional.plugins.redis_cache_plugin',
)
