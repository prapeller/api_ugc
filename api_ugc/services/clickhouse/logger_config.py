import logging
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parent
name = SERVICE_DIR.stem

logger = logging.getLogger(name=name)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s ")

file_handler = logging.FileHandler(SERVICE_DIR / f'{name}.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
