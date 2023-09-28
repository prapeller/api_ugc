import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
name = 'etl_kafka_to_clickhouse'

logger = logging.getLogger(name=name)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ")

file_handler = logging.FileHandler(BASE_DIR / f'{name}.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
