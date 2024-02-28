from copy import copy
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import status
from sqlalchemy import select

from src.models.photos import PhotoModel
from src.models.users import UserModel
from src.conf import messages
from src.services.auth import auth_service

from tests.conftest import TestingSessionLocal, confirmed_user_data

from conftest import test_user


# Mock service for temporarily storing uploaded photos
class MockPhotoService:
    photos = {}

    @classmethod
    def upload_photo(cls, file):
        photo_id = len(cls.photos) + 1
        cls.photos[photo_id] = file
        return photo_id

    @classmethod
    def get_photo(cls, photo_id):
        return cls.photos.get(photo_id)

    @classmethod
    def clear_photos(cls):
        cls.photos = {}


@pytest.mark.asyncio
async def test_upload_photo(client, get_token, monkeypatch):
    mock_cloudinary_uploader_upload = Mock(return_value=('public_id', 'test_public_id'))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )
    files = {"file": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    photo1_data = {
        "description": "test_description_photo1",
        'tags': 'test_tag1'
    }
    response = client.post(
        "api/photos",
        headers={"Authorization": f"Bearer {get_token}"},
        params=photo1_data,
        files=files
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data['public_id'] == 'test_public_id'

    return PhotoModel(**data)
    MockPhotoService.upload_photo(files["file"])


@pytest.mark.asyncio
async def test_add_rate_authenticated_user(client, get_token, monkeypatch):
    photo = await test_upload_photo(client, get_token, monkeypatch)
    photo_id = photo.id
    rate_value = 5

    response = client.post(
        f"/photos/{photo_id}/set-rate",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"value": rate_value}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["value"] == rate_value

    MockPhotoService.get_photo(photo_id)


@pytest.mark.asyncio
async def test_add_rate_unauthenticated_user(client, get_token, monkeypatch):
    photo = await test_upload_photo(client, get_token, monkeypatch)
    photo_id = photo.id
    rate_value = 5

    response = client.post(
        f"/photos/{photo_id}/set-rate",
        json={"value": rate_value}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    MockPhotoService.get_photo(photo_id)


@pytest.mark.asyncio
async def test_add_rate_to_own_photo(client, get_token, monkeypatch):
    photo = await test_upload_photo(client, get_token, monkeypatch)
    photo_id = photo.id
    rate_value = 5

    response = client.post(
        f"/photos/{photo_id}/set-rate",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"value": rate_value}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == messages.RATING_NOT_SET

    MockPhotoService.get_photo(photo_id)


@pytest.mark.asyncio
async def test_add_rate_to_photo_with_invalid_value(client, get_token, monkeypatch):
    photo = await test_upload_photo(client, get_token, monkeypatch)
    photo_id = photo.id
    rate_value = 6

    response = client.post(
        f"/photos/{photo_id}/set-rate",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"value": rate_value}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == messages.INVALID_RATING_VALUE

    MockPhotoService.get_photo(photo_id)
