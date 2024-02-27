import json
from unittest.mock import Mock
import pytest
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from src.models.users import UserModel
from src.conf import messages
from tests.conftest import TestingSessionLocal, unconfirmed_user_data, blocked_user, confirmed_user_data
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
async def test_login_unconfirmed_email(client, create_unconfirmed_user):
    user_data = OAuth2PasswordRequestForm(
        username=unconfirmed_user_data["email"], password=unconfirmed_user_data["password"]
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
async def test_login_blocked_account(client, create_blocked_user):
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
async def test_login_invalid_password(client, create_confirmed_user):

    user_data = OAuth2PasswordRequestForm(
        username=confirmed_user_data["email"], password="wrong_password"
    )
    response = client.post(
        "/api/auth/login",
        data={"username": user_data.username, "password": user_data.password},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD

@pytest.mark.asyncio
async def test_login_valid_account(client):
    user_data = OAuth2PasswordRequestForm(
        username=confirmed_user_data["email"], password=confirmed_user_data["password"]
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
