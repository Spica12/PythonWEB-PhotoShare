import pytest
from copy import copy, deepcopy
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from src.models.photos import TransformedImageLinkModel, PhotoModel
from fastapi import status

from tests.conftest import (
    TestingSessionLocal,
    confirmed_user_data,
    moderator_data,
    create_test_photo,
    create_transform_test_photo,
    get_user_id_by_username,
    create_user_test,
)
from src.services.auth import auth_service
from src.conf import messages


from conftest import test_user


@pytest.mark.asyncio
async def test_delete_photo(client, get_token, monkeypatch):
    mock_cloudinary_uploader_destroy = Mock(return_value={"result": "ok"})
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.destroy_photo",
        mock_cloudinary_uploader_destroy,
    )
    photo = await create_test_photo(test_user["username"])
    user = await get_user_id_by_username(test_user["username"])

    assert photo is not None

    response = client.delete(
        f"api/photos/{photo.id}", headers={"Authorization": f"Bearer {get_token}"}
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(PhotoModel).filter_by(id=photo.id)
        )
        photo = result.scalar_one_or_none()
        assert photo is None

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text


@pytest.mark.asyncio
async def test_delete_photo_not_found(client, get_token, monkeypatch):
    mock_cloudinary_uploader_destroy = Mock(return_value={"result": "ok"})
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.destroy_photo",
        mock_cloudinary_uploader_destroy,
    )
    user = await get_user_id_by_username(test_user["username"])

    photo_id = 99
    response = client.delete(
        f"api/photos/{photo_id}", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == messages.PHOTO_NOT_FOUND
    assert mock_cloudinary_uploader_destroy.assert_not_called


@pytest.mark.asyncio
async def test_delete_photo_user_by_owner(client, monkeypatch, create_confirmed_user):
    mock_cloudinary_uploader_destroy = Mock(return_value={"result": "ok"})
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.destroy_photo",
        mock_cloudinary_uploader_destroy,
    )

    photo = await create_test_photo(confirmed_user_data["username"])
    user = await get_user_id_by_username(confirmed_user_data["username"])

    assert photo is not None

    photo_id = photo.id
    confirmed_user_token = await auth_service.create_access_token(
        confirmed_user_data["email"]
    )

    response = client.delete(
        f"api/photos/{photo_id}",
        headers={"Authorization": f"Bearer {confirmed_user_token}"},
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(PhotoModel).filter_by(id=photo.id)
        )
        photo = result.scalar_one_or_none()
        assert photo is None


    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text
    assert mock_cloudinary_uploader_destroy.assert_called_once


@pytest.mark.asyncio
async def test_delete_photo_user_by_another_user(client, monkeypatch):
    mock_cloudinary_uploader_destroy = Mock(return_value={"result": "ok"})
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.destroy_photo",
        mock_cloudinary_uploader_destroy,
    )
    photo = await create_test_photo(test_user["username"])
    user = await get_user_id_by_username(test_user["username"])

    assert photo is not None

    photo_id = photo.id
    confirmed_user_token = await auth_service.create_access_token(
        confirmed_user_data["email"]
    )

    response = client.delete(
        f"api/photos/{photo_id}",
        headers={"Authorization": f"Bearer {confirmed_user_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
    assert mock_cloudinary_uploader_destroy.assert_called_once
    data = response.json()
    assert data["detail"] == messages.NO_EDIT_RIGHTS
    assert mock_cloudinary_uploader_destroy.assert_not_called


@pytest.mark.asyncio
async def test_delete_photo_transform(client, get_token):
    photo = await create_test_photo(test_user["username"])
    transform_photo = await create_transform_test_photo(photo.id)
    assert transform_photo is not None

    assert transform_photo.photo_id == photo.id
    response = client.delete(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {get_token}"},
        params={"select": "transform", "object_id": transform_photo.id},
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(TransformedImageLinkModel).filter_by(id=transform_photo.id)
        )
        transform_photo = result.scalar_one_or_none()
        assert transform_photo is None

    assert response.status_code == status.HTTP_204_NO_CONTENT
