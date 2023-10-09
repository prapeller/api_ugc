from http import HTTPStatus

import pytest

from core.enums import MethodsEnum
from tests.conftest import test_settings

pytestmark = pytest.mark.asyncio

FILM_BOOKMARKS_URL = f'http://{test_settings.API_UGC_HOST}:{test_settings.API_UGC_PORT}/api/v1/film-bookmarks'


async def test_film_bookmarks_create(body_status, film_uuid):
    bookmark_data = {
        'film_uuid': film_uuid
    }

    body, status = await body_status(
        url=FILM_BOOKMARKS_URL, method=MethodsEnum.post, data=bookmark_data
    )

    assert status == HTTPStatus.OK
    assert body.get('film_uuid') == film_uuid


async def test_film_bookmarks_list_my(body_status):
    body, status = await body_status(url=f'{FILM_BOOKMARKS_URL}/my', method=MethodsEnum.get)

    assert status == HTTPStatus.OK
    assert 'film_bookmarks' in body


async def test_film_bookmarks_delete(body_status, film_uuid):
    body, status = await body_status(
        url=f'{FILM_BOOKMARKS_URL}/{film_uuid}', method=MethodsEnum.delete
    )
    assert status == HTTPStatus.OK
    assert body.get('detail') == 'ok'
