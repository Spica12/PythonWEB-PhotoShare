from unittest.mock import AsyncMock, Mock, patch
import httpx
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
async def test_register_user(client):
    test_user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    # When
    response = client.post("/api/auth/register", json=test_user_data)

    # Then
    assert response.status_code == 201
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

    # When
    # Register the user for the first time
    response = client.post("/api/auth/register", json=test_user_data)

    # Try to register the same user again
    response = client.post("/api/auth/register", json=test_user_data)

    # Then
    assert response.status_code == 409  # Conflict due to existing user
    response_data = response.json()
    assert response_data["detail"] == "Account already exist"

@pytest.mark.asyncio
async def test_register_user_account_exists(client):
    # Макет сервісу аутентифікації
    with patch('src.services.auth.AuthService.get_user_by_email', new_callable=AsyncMock, return_value={
        "id": 1,
        "username": "existinguser",
        "email": "existing@example.com",
        "confirmed": False
    }):

        # Дані для тестування
        user_data = {
            "username": "existinguser",
            "email": "existing@example.com",
            "password": "testpassword"
        }

        # Виклик реєстраційного маршруту через тестовий клієнт
        response = client.post("/api/auth/register", json=user_data)

        # Перевірка статусу відповіді
        assert response.status_code == 409

        # Отримання даних з відповіді
        response_data = response.json()
        assert response_data["detail"] == messages.ACCOUNT_EXIST


@pytest.mark.asyncio
async def test_register_user_username_exists(client):
    # Макет сервісу аутентифікації
    with patch('src.services.auth.AuthService.get_user_by_email', new_callable=AsyncMock, return_value=None):
        with patch('src.services.auth.AuthService.get_user_by_username', new_callable=AsyncMock, return_value={
            "id": 1,
            "username": "existinguser",
            "email": "existing@example.com",
            "confirmed": False
        }):

            # Дані для тестування
            user_data = {
                "username": "existinguser",
                "email": "newuser@example.com",
                "password": "testpassword"
            }

            # Виклик реєстраційного маршруту через тестовий клієнт
            response = client.post("/api/auth/register", json=user_data)

            # Перевірка статусу відповіді
            assert response.status_code == 409

            # Отримання даних з відповіді
            response_data = response.json()
            assert response_data["detail"] == messages.ACCOUNT_EXIST


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
    assert response.status_code == 422

    # Отримання даних з відповіді
    response_data = response.json()
    assert response_data["detail"][0]["msg"].lower() == "field required"



