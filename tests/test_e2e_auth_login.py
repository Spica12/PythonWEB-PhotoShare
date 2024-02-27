import json
from unittest.mock import Mock
import pytest
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from src.models.users import UserModel
from src.conf import messages
from tests.conftest import TestingSessionLocal
from src.services.auth import auth_service


# Перевірка для неправильних даних
def test_login_invalid_credentials(client):
    user_data = OAuth2PasswordRequestForm(
        username="invalid_user@example.com", password="invalid_password"
    )
    response = client.post(
        "/api/auth/login",
        data={"username": user_data.username, "password": user_data.password},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == messages.INVALID_EMAIL


# Check for unconfirmed email
@pytest.mark.asyncio
async def test_login_unconfirmed_email(client):
    unconfirmed_user = {
        "username": "unconfirmed_user@example.com",
        "email": "unconfirmed_user@example.com",
        "password": "test_testpassword",
        "confirmed": False,
        "is_active": True,
        "role": "users",
    }
    async with TestingSessionLocal() as session:
        hash_password = auth_service.get_password_hash(unconfirmed_user["password"])
        new_user = UserModel(
            username=unconfirmed_user["username"],
            email=unconfirmed_user["email"],
            password=hash_password,
            confirmed=unconfirmed_user["confirmed"],
            is_active=unconfirmed_user["is_active"],
            role=unconfirmed_user["role"],
        )
        session.add(new_user)
        await session.commit()

    user_data = OAuth2PasswordRequestForm(
        username=unconfirmed_user["email"], password=unconfirmed_user["password"]
    )
    response = client.post(
        "/api/auth/login",
        data={"username": user_data.username, "password": user_data.password},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == messages.EMAIL_NOT_CONFIRMED


# Перевірка для заблокованого облікового запису
@pytest.mark.asyncio
async def test_login_blocked_account(client):
    blocked_user = {
        "username": "blocked_user@example.com",
        "email": "blocked_user@example.com",
        "password": "test_testpassword",
        "confirmed": True,
        "is_active": False,
        "role": "users",
    }
    async with TestingSessionLocal() as session:
        hash_password = auth_service.get_password_hash(blocked_user["password"])
        new_user = UserModel(
            username=blocked_user["username"],
            email=blocked_user["email"],
            password=hash_password,
            confirmed=blocked_user["confirmed"],
            is_active=blocked_user["is_active"],
            role=blocked_user["role"],
        )
        session.add(new_user)
        await session.commit()

    user_data = OAuth2PasswordRequestForm(
        username=blocked_user["email"], password=blocked_user["password"]
    )
    response = client.post(
        "/api/auth/login",
        data={"username": user_data.username, "password": user_data.password},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_BLOCKED


@pytest.mark.asyncio
async def test_login_invlid_password(client):
    confirmed_user = {
        "username": "confirmed_user@example.com",
        "email": "confirmed_user@example.com",
        "password": "test_testpassword",
        "confirmed": True,
        "is_active": True,
        "role": "users",
    }
    async with TestingSessionLocal() as session:
        hash_password = auth_service.get_password_hash(confirmed_user["password"])
        new_user = UserModel(
            username=confirmed_user["username"],
            email=confirmed_user["email"],
            password=hash_password,
            confirmed=confirmed_user["confirmed"],
            is_active=confirmed_user["is_active"],
            role=confirmed_user["role"],
        )
        session.add(new_user)
        await session.commit()

    user_data = OAuth2PasswordRequestForm(
        username=confirmed_user["email"], password="wrong_password"
    )
    response = client.post(
        "/api/auth/login",
        data={"username": user_data.username, "password": user_data.password},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


def test_login_valid_account(client):
    # Confirmed user was created in previous test
    confirmed_user = {
        "username": "confirmed_user@example.com",
        "email": "confirmed_user@example.com",
        "password": "test_testpassword",
    }
    user_data = OAuth2PasswordRequestForm(
        username=confirmed_user["email"], password=confirmed_user["password"]
    )

    response = client.post(
        "/api/auth/login",
        data={"username": user_data.username, "password": user_data.password},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "access_token"
    assert "refresh_token"
    assert data["token_type"] == "bearer"
