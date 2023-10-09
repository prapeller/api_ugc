from http import HTTPStatus

import pytest

from core.enums import MethodsEnum
from tests.conftest import test_settings

pytestmark = pytest.mark.asyncio

FILM_COMMENTS_URL = f'http://{test_settings.API_UGC_HOST}:{test_settings.API_UGC_PORT}/api/v1/film-comments'


async def test_film_comments_list(body_status, film_uuid):
    body, status = await body_status(url=f'{FILM_COMMENTS_URL}?film_uuid={film_uuid}', method=MethodsEnum.get)

    assert status == HTTPStatus.OK
    assert 'film_comments' in body


async def test_film_comments_read(body_status, comment_uuid):
    body, status = await body_status(url=f'{FILM_COMMENTS_URL}/{comment_uuid}', method=MethodsEnum.get)

    assert status == HTTPStatus.OK
    assert body.get('comment_uuid') == comment_uuid


async def test_film_comments_update(body_status, comment_uuid):
    new_comment = 'new comment'
    comment_data = {'comment': new_comment}
    body, status = await body_status(
        url=f'{FILM_COMMENTS_URL}/{comment_uuid}', method=MethodsEnum.put, data=comment_data
    )
    assert status == HTTPStatus.OK
    assert body.get('comment') == new_comment


async def test_film_comments_create(body_status, film_uuid):
    new_comment = 'new comment'
    comment_data = {'comment': new_comment}
    body, status = await body_status(
        url=f'{FILM_COMMENTS_URL}/?film_uuid={film_uuid}', method=MethodsEnum.post, data=comment_data
    )
    assert status == HTTPStatus.OK
    assert body.get('comment') == new_comment


async def test_film_comments_delete(body_status, comment_uuid):
    body, status = await body_status(
        url=f'{FILM_COMMENTS_URL}/{comment_uuid}', method=MethodsEnum.delete
    )
    assert status == HTTPStatus.OK
    assert body.get('detail') == 'ok'
