from pathlib import Path

import fastapi as fa
from clickhouse_driver.dbapi.cursor import Cursor as CHCursor
from clickhouse_driver.dbapi.errors import Error as CHError

from core.config import settings
from core.logger_config import setup_logger
from db.schemas.user_film_progress import UserFilmProgressReadSerializer

SERVICE_DIR = Path(__file__).resolve().parent
SERVICE_NAME = SERVICE_DIR.stem

logger = setup_logger(SERVICE_NAME, SERVICE_DIR)


class CHRepository():
    def __init__(self, cursor: CHCursor):
        self.cursor: CHCursor = cursor

    def get_last_user_film_progress(self, user_uuid, film_uuid):
        query = f"""select (*) from {settings.CLICKHOUSE_DB}.{settings.USER_FILM_PROGRESS_TABLE}
        where user_uuid = '{user_uuid}' and film_uuid = '{film_uuid}'
        order by created_at desc
        limit 1"""
        try:
            self.cursor.execute(query)
            res = self.cursor.fetchone()
            if not res:
                raise fa.HTTPException(status_code=fa.status.HTTP_404_NOT_FOUND,
                                       detail=f'cant find user_film_progress by {user_uuid=:}, {film_uuid=:}')
            return UserFilmProgressReadSerializer(created_at=res[0],
                                                  user_uuid=user_uuid,
                                                  film_uuid=film_uuid,
                                                  current_time_sec=res[3],
                                                  total_time_sec=res[4])
        except CHError as e:
            logger.error('{}'.format(e))
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f'{e}: {user_uuid=:}, {film_uuid=:}')
