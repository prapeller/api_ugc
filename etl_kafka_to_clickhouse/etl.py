import json
import signal
import sys

import clickhouse_driver
from clickhouse_driver.dbapi.cursor import Cursor as CHCursor
from kafka import KafkaConsumer

import config
from config import settings
from logger_config import logger

BATCH_SIZE = 5
BATCH_FILE_PATH = 'batch.tsv'
insert_query_prefix = (f"INSERT INTO {settings.USER_FILM_PROGRESS_TABLE} "
                       f"(user_uuid, film_uuid, current_time_sec, total_time_sec) VALUES \n")
batch_counter = 0


def get_kafka_consumer_generator():
    consumer = KafkaConsumer(config.KAFKA_USER_FILM_PROGRESS_TOPIC_NAME,
                             bootstrap_servers=config.KAFKA_BROKER_PLAINTEXT_HOST_PORT,
                             enable_auto_commit=False,
                             group_id=settings.USER_FILM_PROGRESS_TABLE)
    try:
        yield consumer
    finally:
        consumer.close()


def get_clickhouse_cursor_generator():
    clickhouse_conn = clickhouse_driver.connect(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        user=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
        database=settings.CLICKHOUSE_DB,
    )
    cursor = clickhouse_conn.cursor()
    cursor.clickhouse_conn = clickhouse_conn
    try:
        yield cursor
    finally:
        cursor.close()
        clickhouse_conn.close()


def load_from_batch_file_to_clickhouse(batch_file_path: str, ch_cursor: CHCursor, consumer: KafkaConsumer) -> None:
    with open(batch_file_path, 'r') as batch_file:
        lines = batch_file.readlines()
        formatted_lines = []
        for line in lines:
            formatted_line = line.strip().replace('\t', "', '")
            formatted_line = "('" + formatted_line + "')"
            formatted_lines.append(formatted_line)
        insert_query_postfix = ',\n'.join(formatted_lines)
        insert_query = insert_query_prefix + insert_query_postfix
        logger.debug(f'ch_cursor.execute: {insert_query=:}')
        ch_cursor.execute(insert_query)
    consumer.commit()
    with open(batch_file_path, 'w') as batch_file:
        batch_file.seek(0)
        batch_file.truncate()


def signal_handler(sig, frame):
    if batch_counter > 0:
        load_from_batch_file_to_clickhouse(BATCH_FILE_PATH, ch_cursor, consumer)
    logger.debug('signal_handler: Received signal {}. Cleaning up...'.format(sig))
    ch_cursor.clickhouse_conn.close()
    logger.debug('signal_handler: clickhouse connection was closed')
    ch_cursor.close()
    logger.debug('signal_handler: clickhouse cursor was closed')
    consumer.close()
    logger.debug('signal_handler: kafka consumer was closed')
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    consumer_gen = get_kafka_consumer_generator()
    ch_cursor_gen = get_clickhouse_cursor_generator()
    consumer = next(consumer_gen)
    ch_cursor = next(ch_cursor_gen)
    logger.debug(f'{consumer=:} is ready! {ch_cursor=:} is ready!')

    for message in consumer:
        logger.debug(f'consuming {message=:}')
        data = json.loads(message.value.decode('utf-8'))
        line = "{}\t{}\t{}\t{}\n".format(data['user_uuid'], data['film_uuid'], data['current_time_sec'],
                                         data['total_time_sec'])
        with open(BATCH_FILE_PATH, 'a') as batch_file:
            batch_file.write(line)
        logger.debug(f'wrote to {BATCH_FILE_PATH}: {line=:}')
        batch_counter += 1
        if batch_counter >= BATCH_SIZE:
            load_from_batch_file_to_clickhouse(BATCH_FILE_PATH, ch_cursor, consumer)
            batch_counter = 0
    if batch_counter > 0:
        load_from_batch_file_to_clickhouse(BATCH_FILE_PATH, ch_cursor, consumer)
