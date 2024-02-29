import pytest
from copy import copy, deepcopy
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from src.models.users import Roles
from src.models.photos import CommentModel, PhotoModel, TransformedImageLinkModel
from fastapi import status

from tests.conftest import (
    TestingSessionLocal,
    confirmed_user_data,
    moderator_data,
    create_test_photo,
    create_transform_test_photo,
    get_user_id_by_username,
    create_test_comment,
    create_user_test,
    create_transform_photo
)
from src.services.auth import auth_service
from src.conf import messages


from conftest import test_user


transformation_template = {
    'width': 200,
    'height': 200,
    'radius': 50,
    'angle': 45,
    'zoom_on_face': True,
    'rotate_photo': False,
    'crop_photo': False,
    'apply_max_radius': False,
    'apply_radius': False,
    'apply_grayscale': False,
}


@pytest.mark.asyncio
async def test_transform_photo_create_by_unknown(client):
    user_data = {
        "username": "tssfst",
        "email": "tedft@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)

    transformation = transformation_template
    transformation['zoom_on_face'] = True

    response = client.post(
        f"api/photos/{photo.id}/transform",
        params={
            'select': 'create',
        },
        json=transformation
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_transform_photo_create_by_user(client):
    user_data = {
        "username": "tsssfst",
        "email": "tedfta@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)

    user_token = await auth_service.create_access_token(
        user.email
    )

    transformation = {
        'width': 200,
        'height': 200,
        'radius': 50,
        'angle': 45,
        'zoom_on_face': True,
        'rotate_photo': True,
        'crop_photo': True,
        'apply_max_radius': False,
        'apply_radius': True,
        'apply_grayscale': True,
}

    response = client.post(
        f"api/photos/{photo.id}/transform",
        headers={'Authorization': f'Bearer {user_token}'},
        params={
            'select': 'create',
        },
        json=transformation
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(TransformedImageLinkModel).filter(
                TransformedImageLinkModel.photo_id == photo.id
            )
        )
        exist_transform_photo = result.scalar_one_or_none()
        assert exist_transform_photo is not None
        assert exist_transform_photo.photo_id == photo.id

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_transform_photo_create_2_by_user(client):
    user_data = {
        "username": "tsssfst9",
        "email": "tedft9a@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)

    user_token = await auth_service.create_access_token(
        user.email
    )

    transformation = {
        'width': 200,
        'height': 200,
        'radius': 50,
        'angle': 45,
        'zoom_on_face': False,
        'rotate_photo': False,
        'crop_photo': False,
        'apply_max_radius': True,
        'apply_radius': False,
        'apply_grayscale': False,
}

    response = client.post(
        f"api/photos/{photo.id}/transform",
        headers={'Authorization': f'Bearer {user_token}'},
        params={
            'select': 'create',
        },
        json=transformation
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(TransformedImageLinkModel).filter(
                TransformedImageLinkModel.photo_id == photo.id
            )
        )
        exist_transform_photo = result.scalar_one_or_none()
        assert exist_transform_photo is not None
        assert exist_transform_photo.photo_id == photo.id

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_transform_photo_create_not_found_by_user(client):
    user_data = {
        "username": "tssssfst",
        "email": "tedftaa@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)

    user_token = await auth_service.create_access_token(
        user.email
    )

    transformation = transformation_template
    transformation['zoom_on_face'] = True
    not_exist_photo_id = 666

    response = client.post(
        f"api/photos/{not_exist_photo_id}/transform",
        headers={'Authorization': f'Bearer {user_token}'},
        params={
            'select': 'create',
        },
        json=transformation
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(TransformedImageLinkModel).filter(
                TransformedImageLinkModel.photo_id == not_exist_photo_id
            )
        )
        exist_transform_photo = result.scalar_one_or_none()
        assert exist_transform_photo is None

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_transform_photo_create_by_another_user(client):
    user_data = {
        "username": "tsssddvfst",
        "email": "tedftbwa@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    another_user_data = {
        "username": "tsssfsssst",
        "email": "tedftaaas@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    another_user = await create_user_test(**another_user_data)
    photo = await create_test_photo(user.username)

    another_user_token = await auth_service.create_access_token(
        another_user.email
    )

    transformation = transformation_template
    transformation['zoom_on_face'] = True

    response = client.post(
        f"api/photos/{photo.id}/transform",
        headers={'Authorization': f'Bearer {another_user_token}'},
        params={
            'select': 'create',
        },
        json=transformation
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(TransformedImageLinkModel).filter(
                TransformedImageLinkModel.photo_id == photo.id
            )
        )
        exist_transform_photo = result.scalar_one_or_none()
        assert exist_transform_photo is None

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response_data = response.json()
    assert data['detail'] == messages.UNKNOWN_PARAMETER


@pytest.mark.asyncio
async def test_transform_photo_qrcode_by_user(client):
    user_data = {
        "username": "tsssdaadvfst",
        "email": "tedftbczzwa@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)

    user_token = await auth_service.create_access_token(
        user.email
    )

    transform_photo = await create_transform_photo(photo.id)
    transformation = transformation_template
    transformation['zoom_on_face'] = True

    response = client.post(
        f"api/photos/{photo.id}/transform",
        headers={'Authorization': f'Bearer {user_token}'},
        params={
            'select': 'qrcode',
            'object_id': transform_photo.id,
        },
        json=transformation_template
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(TransformedImageLinkModel).filter(
                TransformedImageLinkModel.photo_id == photo.id
            )
        )
        exist_transform_photo = result.scalar_one_or_none()
        assert exist_transform_photo.id == transform_photo.id
        assert exist_transform_photo is not None
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_get_transform_photo_url_by_user(client):
    user_data = {
        "username": "tsssdaadvf2st",
        "email": "tedftbczzw2a@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)

    user_token = await auth_service.create_access_token(
        user.email
    )

    transform_photo = await create_transform_photo(photo.id)
    transformation = transformation_template

    response = client.get(
        f"api/photos/{photo.id}/transform",
        headers={'Authorization': f'Bearer {user_token}'},
        params={
            'select': 'url',
            'object_id': transform_photo.id,
        },
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(TransformedImageLinkModel).filter(
                TransformedImageLinkModel.photo_id == photo.id
            )
        )
        exist_transform_photo = result.scalar_one_or_none()
        assert exist_transform_photo.id == transform_photo.id
        assert exist_transform_photo is not None

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_transform_photo_qrcode_by_user(client):
    user_data = {
        "username": "4tsssdaadvf2st",
        "email": "te4dftbczzw2a@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)

    user_token = await auth_service.create_access_token(
        user.email
    )
    photo_id = photo.id
    transform_photo = await create_transform_photo(photo_id)

    response = client.get(
        f"api/photos/{photo.id}/transform",
        headers={'Authorization': f'Bearer {user_token}'},
        params={
            'select': 'qrcode',
            'object_id': transform_photo.id,
        },
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(TransformedImageLinkModel).filter(
                TransformedImageLinkModel.photo_id == photo.id
            )
        )
        exist_transform_photo = result.scalar_one_or_none()
        assert exist_transform_photo.id == transform_photo.id
        assert exist_transform_photo is not None

    assert response.status_code == status.HTTP_200_OK
