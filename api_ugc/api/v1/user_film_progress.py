import fastapi as fa
import pydantic as pd
from aiokafka import AIOKafkaProducer

from core import config
from core.dependencies import current_user_uuid_dependency, aiokafka_producer_dependency, clickhouse_repo_dependency
from db.schemas.user_film_progress import UserFilmProgressReadSerializer
from services.clickhouse.clickhouse_repository import CHRepository

router = fa.APIRouter()


@router.post('/')
async def user_film_progress_create(
        aiokafka_producer: AIOKafkaProducer = fa.Depends(aiokafka_producer_dependency),
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        film_uuid: pd.UUID4 = fa.Body(...),
        current_time_sec: int = fa.Body(...),
        total_time_sec: int = fa.Body(...),
):
    user_uuid, film_uuid = str(user_uuid), str(film_uuid)
    key = f'{user_uuid}_{film_uuid}'.encode('utf-8')
    message_dict = {
        'user_uuid': user_uuid,
        'film_uuid': film_uuid,
        'current_time_sec': current_time_sec,
        'total_time_sec': total_time_sec,
    }
    await aiokafka_producer.send(topic=config.KAFKA_USER_FILM_PROGRESS_TOPIC_NAME, key=key, value=message_dict)
    return message_dict


@router.get('/{film_uuid}',
            response_model=UserFilmProgressReadSerializer)
async def user_film_progress(
        film_uuid: pd.UUID4,
        user_uuid: pd.UUID4 = fa.Depends(current_user_uuid_dependency),
        ch_repo: CHRepository = fa.Depends(clickhouse_repo_dependency)
):
    return ch_repo.get_last_user_film_progress(user_uuid, film_uuid)
