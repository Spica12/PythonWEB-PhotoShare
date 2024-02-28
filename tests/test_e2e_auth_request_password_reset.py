from unittest.mock import AsyncMock, Mock, MagicMock
from fastapi import BackgroundTasks
from unittest import mock
import json

import pytest
from sqlalchemy import select

import src.services.email
from src.models.users import UserModel
from tests.conftest import TestingSessionLocal, test_user, TestClient
from src.conf import messages
from fastapi.security import OAuth2PasswordRequestForm
from src.services.auth import auth_service
from src.services.email import EmailService
from fastapi import status
from src.models.users import UserModel
from src.schemas.users import RequestPasswordResetSchema
from pydantic import BaseModel, EmailStr
from src.repositories.users import UserRepo


@pytest.mark.asyncio
async def test_request_password_reset(client: TestClient, monkeypatch):
    # Given
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    # Mocking the get_user_by_email method
    mock_get_user_by_email = AsyncMock()
    mock_get_user_by_email.return_value = UserModel(confirmed=True, **user_data)

    # Mocking the send_request_password_mail method
    mock_send_request_password_mail = MagicMock()

    monkeypatch.setattr(auth_service, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(
        "src.services.email.EmailService.send_request_password_mail",
        mock_send_request_password_mail,
    )

    # When
    response = client.post("/api/auth/password-reset", json=user_data)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Password reset request sent"}

    # Check if the necessary functions were called
    mock_get_user_by_email.assert_called_once_with(user_data["email"], mock.ANY)
    mock_send_request_password_mail.assert_called_once_with(
        user_data["email"], user_data["username"], mock.ANY
    )













@pytest.mark.asyncio
async def test_request_password_reset_email_not_confirmed(client, monkeypatch):
    # Given
    existing_user_data = {
        "username": "existing_user",
        "email": "existing@example.com",
        "confirmed": False,
    }

    # Mock the necessary functions
    monkeypatch.setattr(auth_service, "get_user_by_email", AsyncMock(return_value=UserModel(**existing_user_data)))

    # When
    response_reset = client.post("/api/auth/password-reset", json=existing_user_data)

    # Then
    assert response_reset.status_code == status.HTTP_401_UNAUTHORIZED
    response_data_reset = response_reset.json()
    assert response_data_reset["detail"] == "Email not confirmed"










@pytest.mark.asyncio
async def test_request_password_reset_invalid_username(client, monkeypatch):
    # Given
    existing_user_data = {
        "username": "existing_user",
        "email": "existing@example.com",
        "confirmed": True,
    }
    invalid_username_data = {
        "username": "invalid_username",
        "email": "existing@example.com",
    }

    # Mock the necessary functions
    monkeypatch.setattr(auth_service, "get_user_by_email", AsyncMock(return_value=UserModel(**existing_user_data)))

    # When
    response_reset = client.post("/api/auth/password-reset", json=invalid_username_data)

    # Then
    assert response_reset.status_code == status.HTTP_400_BAD_REQUEST
    response_data_reset = response_reset.json()
    assert response_data_reset["detail"] == "Invalid username"







