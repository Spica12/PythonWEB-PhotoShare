import pytest
from copy import copy, deepcopy
from unittest.mock import AsyncMock, Mock
import asyncio

import pytest
from sqlalchemy import select
from src.models.photos import CommentModel, PhotoModel, TransformedImageLinkModel
from src.models.users import UserModel
from fastapi import status

from tests.conftest import TestingSessionLocal, confirmed_user_data, moderator_data
from src.services.auth import auth_service
from src.conf import messages


from conftest import test_user

async def create_test_photo(username: str):
    async with TestingSessionLocal() as session:
        result = await session.execute(select(UserModel).filter_by(username=username))
        current_user = result.scalar_one_or_none()
        photo = PhotoModel(
            user_id=current_user.id,
            description="test_description",
            image_url="test_url",
            public_id="test_public_id",
        )
        session.add(photo)
        await session.commit()
        await session.refresh(photo)
    return photo


async def create_transform_test_photo(photo_id: int):
    async with TestingSessionLocal() as session:
        result = await session.execute(select(PhotoModel).filter_by(id=photo_id))
        exist_photo = result.scalars().first()
        transform_photo = TransformedImageLinkModel(
            photo_id=exist_photo.id,
            image_url="test_url",
        )
        session.add(transform_photo)
        await session.commit()
        await session.refresh(transform_photo)
    return transform_photo


async def get_user_id_by_username(username: str):
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=username)
        )
        user = result.scalar_one_or_none()
        return user.id


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
async def test_delete_photo_user_by_moderator(client, monkeypatch, create_moderator):
    mock_cloudinary_uploader_destroy = Mock(return_value={"result": "ok"})
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.destroy_photo",
        mock_cloudinary_uploader_destroy,
    )
    photo = await create_test_photo(confirmed_user_data["username"])
    user = await get_user_id_by_username(confirmed_user_data["username"])

    assert photo is not None

    photo_id = photo.id
    moderator_token = await auth_service.create_access_token(moderator_data["email"])

    response = client.delete(
        f"api/photos/{photo_id}",
        headers={"Authorization": f"Bearer {moderator_token}"},
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(select(PhotoModel).filter_by(id=photo.id))
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
