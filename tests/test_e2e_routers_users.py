from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import select
from src.models.users import UserModel
from tests.conftest import TestingSessionLocal, test_user
from src.conf import messages
from pathlib import Path
from src.services.auth import auth_service


user_data = {
    "username": "string",
    "email": "user@example.com",
    "password": "string",
    "avatar": "user_data_avatar",
    "role": "moderator",
    "confirmed": True,
    "is_active": True,
}


@pytest.mark.asyncio
async def test_get_current_user_not_authenticated(client):
    response = client.get("api/users/my_profile")
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_AUTHENTICATED


@pytest.mark.asyncio
async def test_get_current_user(client, get_token):
    response = client.get(
        "api/users/my_profile",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert data["avatar"] == test_user["avatar"]
    assert data["role"] == test_user["role"]
    # assert data["confirmed"] == test_user["confirmed"]
    # assert data["is_active"] == test_user["is_active"]


@pytest.mark.asyncio
async def test_get_user_not_found(client, get_token):

    response = client.get(
        f"api/users/{user_data['username']}",
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    print(data)
    assert data["detail"] == messages.ACCOUNT_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user(client, get_token):
    async with TestingSessionLocal() as session:
        copy_user_data = user_data.copy()
        copy_user_data["password"] = auth_service.get_password_hash(
            user_data["password"]
        )
        user = UserModel(**copy_user_data)
        session.add(user)
        await session.commit()

    response = client.get(
        f"api/users/{user_data['username']}",
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["username"] == user_data["username"]
    # assert data["email"] == user_data["email"]
    assert data["avatar"] == user_data["avatar"]
    assert data["role"] == user_data["role"]
    # assert data["confirmed"] == test_user["confirmed"]
    # assert data["is_active"] == test_user["is_active"]


@pytest.mark.asyncio
async def test_update_current_user_not_authenticated(client):
    response = client.put(
        f"api/users/my_profile",
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_AUTHENTICATED


@pytest.mark.asyncio
async def test_get_current_user_not_authenticated(client):
    response = client.put("api/users/my_profile")
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_AUTHENTICATED


@pytest.mark.asyncio
async def test_get_user_change_email_wrong_password(client, get_token):
    test_data = {
        "email": "testemail@example.com",
        "confirm_password": "wrong_password",
    }
    response = client.put(
        "api/users/my_profile/email",
        headers={"Authorization": f"Bearer {get_token}"},
        params=test_data,
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


@pytest.mark.asyncio
async def test_get_user_change_email(client, get_token):
    test_data = {
        "email": "testemail@example.com",
        "confirm_password": test_user["password"],
    }
    response = client.put(
        "api/users/my_profile/email",
        headers={"Authorization": f"Bearer {get_token}"},
        params=test_data,
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["username"] == test_user["username"]
    assert data["email"] == test_data["email"]
    assert data["avatar"] == test_user["avatar"]
    assert data["role"] == test_user["role"]
    # assert data["confirmed"] == test_user["confirmed"]
    # assert data["is_active"] == test_user["is_active"]


@pytest.mark.asyncio
async def test_get_user_change_avatar_wrong_password(client, monkeypatch):
    access_token = await auth_service.create_access_token(user_data["email"])
    mock_cloudinary_upload_avatar = Mock(return_value="test_avatarimage.jpg")
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_avatar",
        mock_cloudinary_upload_avatar,
    )
    test_data = {
        "confirm_password": "wrong_password",
    }
    files = {"avatar": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    response = client.put(
        "api/users/my_profile/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
        params=test_data,
        files=files,
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


@pytest.mark.asyncio
async def test_get_user_change_avatar(client, monkeypatch):
    access_token = await auth_service.create_access_token(user_data["email"])
    mock_cloudinary_upload_avatar = Mock(return_value="test_avatarimage.jpg")
    monkeypatch.setattr(
        "src.services.cloudinary.CloudinaryService.upload_avatar",
        mock_cloudinary_upload_avatar,
    )
    test_data = {
        "confirm_password": user_data["password"],
    }
    files = {"avatar": ("test_image.jpg", open(Path("tests") / "test_image.jpg", "rb"))}
    response = client.put(
        "api/users/my_profile/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
        params=test_data,
        files=files,
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["avatar"] == "test_avatarimage.jpg"
    assert data["role"] == user_data["role"]
    # assert data["confirmed"] == user_data["confirmed"]
    # assert data["is_active"] == user_data["is_active"]


@pytest.mark.asyncio
async def test_update_user_is_not_active_by_admin(client):
    async with TestingSessionLocal() as session:

        hash_password = auth_service.get_password_hash("admin_password")
        admin_data = {
            "username": "admin_username",
            "email": "admin_email@example.com",
            "password": hash_password,
            "avatar": "admin_avatar",
            "role": "admin",
            "confirmed": True,
            "is_active": True,
        }
        hash_password = auth_service.get_password_hash("user_password")
        user_data2 = {
            "username": "user_username",
            "email": "user_email@example.com",
            "password": hash_password,
            "avatar": "user_avatar",
            "role": "users",
            "confirmed": True,
            "is_active": True,
        }
        admin = UserModel(**admin_data)
        user = UserModel(**user_data2)
        session.add(admin)
        session.add(user)
        await session.commit()

    change_data_for_user = {"is_active": False, "role": "users"}

    access_token = await auth_service.create_access_token(admin_data["email"])

    response = client.put(
        f'api/users/{user_data2["username"]}',
        headers={"Authorization": f"Bearer {access_token}"},
        params=change_data_for_user,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "user_username"
    assert data["email"] == "user_email@example.com"
    assert data["avatar"] == "user_avatar"
    assert data["role"] == change_data_for_user["role"]
    assert data["is_active"] is change_data_for_user["is_active"]
    assert data["confirmed"] is True


@pytest.mark.asyncio
async def test_update_user_is_active_by_user(client):
    admin_data = {
        "username": "admin_username",
        "email": "admin_email@example.com",
    }
    user_data2 = {
        "username": "user_username",
        "email": "user_email@example.com",
    }

    change_data_for_user = {"is_active": False, "role": "users"}

    access_token = await auth_service.create_access_token(user_data2["email"])

    response = client.put(
        f'api/users/{user_data2["username"]}',
        headers={"Authorization": f"Bearer {access_token}"},
        params=change_data_for_user,
    )

    assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_update_user_is_active_and_moderator_by_admin(client):
    admin_data = {
        "username": "admin_username",
        "email": "admin_email@example.com",
    }
    user_data = {
        "username": "user_username",
        "email": "user_email@example.com",
    }

    change_data_for_user = {"is_active": False, "role": "moderator"}

    access_token = await auth_service.create_access_token(admin_data["email"])

    response = client.put(
        f'api/users/{user_data["username"]}',
        headers={"Authorization": f"Bearer {access_token}"},
        params=change_data_for_user,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "user_username"
    assert data["email"] == "user_email@example.com"
    assert data["avatar"] == "user_avatar"
    assert data["role"] == change_data_for_user["role"]
    assert data["is_active"] is change_data_for_user["is_active"]
    assert data["confirmed"] is True


@pytest.mark.asyncio
async def test_update_user_is_active_and_admin_by_admin(client):
    admin_data = {
        "username": "admin_username",
        "email": "admin_email@example.com",
    }
    user_data = {
        "username": "user_username",
        "email": "user_email@example.com",
    }

    change_data_for_user = {"is_active": True, "role": "admin"}

    access_token = await auth_service.create_access_token(admin_data["email"])

    response = client.put(
        f'api/users/{user_data["username"]}',
        headers={"Authorization": f"Bearer {access_token}"},
        params=change_data_for_user,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "user_username"
    assert data["email"] == "user_email@example.com"
    assert data["avatar"] == "user_avatar"
    assert data["role"] == change_data_for_user["role"]
    assert data["is_active"] is change_data_for_user["is_active"]
    assert data["confirmed"] is True


@pytest.mark.asyncio
async def test_update_user_confirmed_false_by_admin(client):
    admin_data = {
        "username": "admin_username",
        "email": "admin_email@example.com",
    }
    user_data = {
        "username": "user_username",
        "email": "user_email@example.com",
    }

    change_data_for_user = {"confirmed": False}

    access_token = await auth_service.create_access_token(admin_data["email"])

    response = client.put(
        f'api/users/{user_data["username"]}',
        headers={"Authorization": f"Bearer {access_token}"},
        params=change_data_for_user,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "user_username"
    assert data["email"] == "user_email@example.com"
    assert data["avatar"] == "user_avatar"
    assert data["role"] == "users"
    assert data["is_active"] is True
    assert data["confirmed"] is change_data_for_user["confirmed"]


@pytest.mark.asyncio
async def test_update_user_confirmed_false_by_admin(client):
    admin_data = {
        "username": "admin_username",
        "email": "admin_email@example.com",
    }
    user_data = {
        "username": "user_username",
        "email": "user_email@example.com",
    }

    change_data_for_user = {"confirmed": True}

    access_token = await auth_service.create_access_token(admin_data["email"])

    response = client.put(
        f'api/users/{user_data["username"]}',
        headers={"Authorization": f"Bearer {access_token}"},
        params=change_data_for_user,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "user_username"
    assert data["email"] == "user_email@example.com"
    assert data["avatar"] == "user_avatar"
    assert data["role"] == "users"
    assert data["is_active"] is True
    assert data["confirmed"] is change_data_for_user["confirmed"]
