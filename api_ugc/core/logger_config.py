import logging
from pathlib import Path

import logstash
from core.config import settings
from core.shared import RequestIdFilter

def setup_logger(service_name: str, service_dir: Path):
    logger = logging.getLogger(name=service_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s ')

    file_handler = logging.FileHandler(service_dir / f'{service_name}.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.addHandler(logstash.LogstashHandler(settings.LOGSTASH_HOST, settings.LOGSTASH_PORT, version=1))
    logger.addFilter(RequestIdFilter())

    return logger