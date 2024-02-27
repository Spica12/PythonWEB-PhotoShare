from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import select
from src.models.photos import PhotoModel
from src.models.users import UserModel
from fastapi import status

from tests.conftest import TestingSessionLocal
from src.services.auth import auth_service
from src.conf import messages


from conftest import test_user


user1_data = {
    "username": "user1",
    "email": "user1@example.com",
    "password": "test_testpassword",
    "confirmed": True,
    "is_active": True,
    "role": "users",
}
user2_data = {
    "username": "user2",
    "email": "user2@example.com",
    "password": "test_testpassword",
    "confirmed": True,
    "is_active": True,
    "role": "users",
}


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


    # async with TestingSessionLocal() as session:
    #     hash_password_user1 = auth_service.get_password_hash(user1_data["password"])
    #     user1 = UserModel(
    #         username=user1_data["username"],
    #         email=user1_data["email"],
    #         password=hash_password_user1,
    #         confirmed=user1_data["confirmed"],
    #         is_active=user1_data["is_active"],
    #         role=user1_data["role"],
    #     )
    #     hash_password_user2 = auth_service.get_password_hash(user1_data["password"])
    #     user2 = UserModel(
    #         username=user1_data["username"],
    #         email=user1_data["email"],
    #         password=hash_password_user2,
    #         confirmed=user1_data["confirmed"],
    #         is_active=user1_data["is_active"],
    #         role=user1_data["role"],
    #     )
    #     session.add(user1)
    #     session.add(user2)
    #     await session.commit()
    #     await session.refresh(user1)
    #     await session.refresh(user2)

    #     for i in range(25):
    #         photo = PhotoModel(
    #             user_id=user1.id,
    #             description=f"test_description_photo{i}",
    #             image_url=f"test_photo{i}url",
    #         )

    #         session.add(photo)
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



# @pytest.mark.asyncio
# async def test_show_all_photos(client):
#     ..
