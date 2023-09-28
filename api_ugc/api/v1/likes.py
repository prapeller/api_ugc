import fastapi as fa
from aiokafka import AIOKafkaProducer

from core import config
from core.dependencies import get_current_user_id_dependency, get_aiokafka_producer_dependency

router = fa.APIRouter()


@router.post('/')
async def user_film_progress_create(
        aiokafka_producer: AIOKafkaProducer = fa.Depends(get_aiokafka_producer_dependency),
        user_uuid: str = fa.Depends(get_current_user_id_dependency),
        film_uuid: str = fa.Body(...),
        current_time_sec: str = fa.Body(...),
        total_time_sec: str = fa.Body(...),
):
    key = f'{user_uuid}_{film_uuid}'.encode('utf-8')
    message_dict = {
        'user_uuid': user_uuid,
        'film_uuid': film_uuid,
        'current_time_sec': int(current_time_sec),
        'total_time_sec': int(total_time_sec),
    }
    await aiokafka_producer.send(topic=config.KAFKA_USER_FILM_PROGRESS_TOPIC_NAME, key=key, value=message_dict)
    return message_dict


@router.get('/{film_id}')
async def user_film_progress_create(
        film_id: str,
        user_id: str = fa.Depends(get_current_user_id_dependency),
):
    pass
