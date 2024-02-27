from copy import copy
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import select
from src.models.photos import PhotoModel
from src.models.users import UserModel
from fastapi import status

from tests.conftest import TestingSessionLocal, confirmed_user_data
from src.services.auth import auth_service
from src.conf import messages


from conftest import test_user


@pytest.mark.asyncio
async def test_upload_photo_with_five_tags(client, get_token, monkeypatch):
    mock_cloudinary_uploader_upload = Mock(return_value=('public_id', 'test_public_id'))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )
    files = {"file": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    photo1_data = {
        "description": "test_description_photo1",
        'tags': 'test_tag1, test_tag2, test_tag3, test_tag4, test_tag5'
    }
    response = client.post(
        "api/photos",
        headers={"Authorization": f"Bearer {get_token}"},
        params=photo1_data,
        files=files
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()

    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data['public_id'] == 'test_public_id'
    # assert data["user_id"] == user.id
    # assert data["description"] == photo1_data["description"]
    # assert data["image_url"] == 'test_public_id'
    # assert ['rating'] is None
    # assert data["tags"] == ['test_tag1']
    # assert data["comments"] == []
    assert mock_cloudinary_uploader_upload.called


@pytest.mark.asyncio
async def test_upload_photo_with_more_five_tags(client, get_token, monkeypatch):
    mock_cloudinary_uploader_upload = Mock(return_value=('public_id', 'test_public_id'))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )
    files = {"file": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    photo1_data = {
        "description": "test_description_photo1",
        'tags': 'test_tag1, test_tag2, test_tag3, test_tag4, test_tag5, test_tag6'
    }

    response = client.post(
        "api/photos",
        headers={"Authorization": f"Bearer {get_token}"},
        params=photo1_data,
        files=files
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
    data = response.json()
    assert data['detail'] == messages.TOO_MANY_TAGS
    mock_cloudinary_uploader_upload.assert_not_called()

@pytest.mark.asyncio
async def test_upload_photo_with_one_tag(client, get_token, monkeypatch):
    mock_cloudinary_uploader_upload = Mock(return_value=('public_id', 'test_public_id'))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )
    files = {"file": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    photo1_data = {
        "description": "test_description_photo1",
        'tags': '  test tag1  '
    }

    response = client.post(
        "api/photos",
        headers={"Authorization": f"Bearer {get_token}"},
        params=photo1_data,
        files=files
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()

    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data['public_id'] == 'test_public_id'
    assert mock_cloudinary_uploader_upload.called


@pytest.mark.asyncio
async def test_upload_photo_without_tags(client, get_token, monkeypatch):
    mock_cloudinary_uploader_upload = Mock(return_value=('public_id', 'test_public_id'))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )

    files = {"file": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    photo1_data = {
        "description": "test_description_photo1",
        'tags': ''
    }

    response = client.post(
        "api/photos",
        headers={"Authorization": f"Bearer {get_token}"},
        params=photo1_data,
        files=files
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()

    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data['public_id'] == 'test_public_id'
    # assert data["user_id"] == user.id
    # assert data["description"] == photo1_data["description"]
    # assert data["image_url"] == 'test_public_id'
    # assert ['rating'] is None
    # assert data["tags"] == ['test_tag1']
    # assert data["comments"] == []
    assert mock_cloudinary_uploader_upload.called



@pytest.mark.asyncio
async def test_show_all_photos(client):
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()

    response = client.get("api/photos")

    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_show_photo(client):
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()
    photo_id = 3
    response = client.get("api/photos", params={"photo_id": photo_id})

    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()


# @pytest.mark.asyncio
# async def test_show_photo_not_found(client):
#     async with TestingSessionLocal() as session:
#         result = await session.execute(
#             select(UserModel).filter_by(username=test_user["username"])
#         )
#         user = result.scalar_one_or_none()
#     photo_id = 10
#     response = client.get("api/photos", params={"photo_id": photo_id})

#     assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
#     data = response.json()
#     # assert data['detail'] == messages.PHOTO_NOT_FOUND
