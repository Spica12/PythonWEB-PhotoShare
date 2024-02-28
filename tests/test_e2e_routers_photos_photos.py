from copy import copy, deepcopy
from pathlib import Path
from unittest.mock import AsyncMock, Mock
from PIL import Image
import io

import pytest
from sqlalchemy import select
from src.models.photos import CommentModel, PhotoModel, TransformedImageLinkModel
from src.models.users import UserModel
from fastapi import status

from tests.conftest import TestingSessionLocal, confirmed_user_data, moderator_data
from src.services.auth import auth_service
from src.conf import messages


from conftest import test_user



@pytest.mark.asyncio
async def test_upload_photo_with_five_tags(client, get_token, monkeypatch):
    mock_cloudinary_uploader_upload = Mock(return_value=("public_id", "test_public_id"))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )
    files = {"file": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    photo1_data = {
        "description": "test_description_photo1",
        "tags": "test_tag1, test_tag2, test_tag3, test_tag4, test_tag5",
    }
    response = client.post(
        "api/photos",
        headers={"Authorization": f"Bearer {get_token}"},
        params=photo1_data,
        files=files,
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()

    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["public_id"] == "test_public_id"
    # assert data["user_id"] == user.id
    # assert data["description"] == photo1_data["description"]
    # assert data["image_url"] == 'test_public_id'
    # assert ['rating'] is None
    # assert data["tags"] == ['test_tag1']
    # assert data["comments"] == []
    assert mock_cloudinary_uploader_upload.called


@pytest.mark.asyncio
async def test_upload_photo_with_more_five_tags(client, get_token, monkeypatch):
    mock_cloudinary_uploader_upload = Mock(return_value=("public_id", "test_public_id"))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )
    files = {"file": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    photo1_data = {
        "description": "test_description_photo1",
        "tags": "test_tag1, test_tag2, test_tag3, test_tag4, test_tag5, test_tag6",
    }

    response = client.post(
        "api/photos",
        headers={"Authorization": f"Bearer {get_token}"},
        params=photo1_data,
        files=files,
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
    data = response.json()
    assert data["detail"] == messages.TOO_MANY_TAGS
    mock_cloudinary_uploader_upload.assert_not_called()


@pytest.mark.asyncio
async def test_upload_photo_with_one_tag(client, get_token, monkeypatch):
    mock_cloudinary_uploader_upload = Mock(return_value=("public_id", "test_public_id"))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )
    files = {"file": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    photo1_data = {"description": "test_description_photo1", "tags": "  test tag1  "}

    response = client.post(
        "api/photos",
        headers={"Authorization": f"Bearer {get_token}"},
        params=photo1_data,
        files=files,
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()

    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["public_id"] == "test_public_id"
    assert mock_cloudinary_uploader_upload.called


@pytest.mark.asyncio
async def test_upload_photo_without_tags(client, get_token, monkeypatch):
    mock_cloudinary_uploader_upload = Mock(return_value=("public_id", "test_public_id"))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )

    files = {"file": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    photo1_data = {"description": "test_description_photo1", "tags": ""}

    response = client.post(
        "api/photos",
        headers={"Authorization": f"Bearer {get_token}"},
        params=photo1_data,
        files=files,
    )
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()

    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["public_id"] == "test_public_id"
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
    for photo in data:
        assert photo["description"]
        assert photo["image_url"]
        assert photo["tags"]


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content_type, expected_status_code",
    [
        ("image/jpg", status.HTTP_201_CREATED),
        ("image/jpeg", status.HTTP_201_CREATED),
        ("image/png", status.HTTP_201_CREATED),
        ("plain/text", status.HTTP_400_BAD_REQUEST),
    ],
)
async def test_upload_photo_validate(
    client, monkeypatch, get_token, content_type, expected_status_code
):
    mock_cloudinary_uploader_upload = Mock(return_value=("public_id", "test_public_id"))
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_photo",
        mock_cloudinary_uploader_upload,
    )
    # Створюємо тестовий файл зображення
    img = Image.new("RGB", (100, 100), color="red")
    img_io = io.BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)
    b = img_io.read()

    photo1_data = {"description": "test_description_photo1", "tags": ""}

    response = client.post(
        "api/photos",
        headers={
            "Authorization": f"Bearer {get_token}",
        },
        params=photo1_data,
        files={"file": ("test_image.png", img_io, content_type)},
    )

    assert response.status_code == expected_status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "photo_id, status_code, detail_code",
    [
        (1, 200, "OK"),
        (2, 200, "OK"),
        (3, 200, "OK"),
        (4, 404, messages.PHOTO_NOT_FOUND),
    ],
)
async def test_show_photo(client, photo_id, status_code, detail_code):
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(UserModel).filter_by(username=test_user["username"])
        )
        user = result.scalar_one_or_none()
    response = client.get(f"api/photos/{photo_id}")

    assert response.status_code == status_code, response.text
    data = response.json()
    if response.status_code != status.HTTP_200_OK:
        assert data["detail"] == detail_code
