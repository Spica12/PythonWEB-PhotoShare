from unittest.mock import AsyncMock, Mock, patch
import httpx
import pytest
from sqlalchemy import select
from src.models.users import UserModel
from tests.conftest import TestingSessionLocal, test_user
from src.conf import messages
from pathlib import Path
from src.services.auth import auth_service
from fastapi import status


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
async def test_register_user(client):
    test_user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    # When
    response = client.post("/api/auth/register", json=test_user_data)

    # Then
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert "id" in response_data
    assert "username" in response_data
    assert "email" in response_data
    assert "confirmed" in response_data

@pytest.mark.asyncio
async def test_register_existing_user_by_email(client):
    test_user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    # Try to register the same user again
    response = client.post("/api/auth/register", json=test_user_data)

    # Then
    assert response.status_code == status.HTTP_409_CONFLICT, response.text# Conflict due to existing user
    response_data = response.json()
    assert response_data["detail"] == messages.ACCOUNT_EXIST

@pytest.mark.asyncio
async def test_register_user_by_username(client):
    # Макет сервісу аутентифікації

    # Дані для тестування
    user_data = {
        "username": "testuser",
        "email": "existing@example.com",
        "password": "testpassword"
    }

    # Виклик реєстраційного маршруту через тестовий клієнт
    response = client.post("/api/auth/register", json=user_data)

    # Перевірка статусу відповіді
    assert response.status_code == status.HTTP_409_CONFLICT

    # Отримання даних з відповіді
    response_data = response.json()
    assert response_data["detail"] == messages.ACCOUNT_EXIST


# @pytest.mark.asyncio
# async def test_register_user_username_exists(client):
#     # Макет сервісу аутентифікації

#     # Дані для тестування
#     user_data = {
#         "username": "testuser",
#         "email": "newuser@example.com",
#         "password": "testpassword"
#     }

#     # Виклик реєстраційного маршруту через тестовий клієнт
#     response = client.post("/api/auth/register", json=user_data)

#     # Перевірка статусу відповіді
#     assert response.status_code == status.HTTP_409_CONFLICT

#     # Отримання даних з відповіді
#     response_data = response.json()
#     assert response_data["detail"] == messages.ACCOUNT_EXIST


@pytest.mark.asyncio
async def test_register_user_invalid_data(client):
    # Дані для тестування з невірними даними (наприклад, відсутність пароля)
    invalid_user_data = {
        "username": "testuser",
        "email": "test@example.com"
    }

    # Виклик реєстраційного маршруту через тестовий клієнт
    response = client.post("/api/auth/register", json=invalid_user_data)

    # Перевірка статусу відповіді
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Отримання даних з відповіді
    response_data = response.json()
    assert response_data["detail"][0]["msg"].lower() == "field required"
