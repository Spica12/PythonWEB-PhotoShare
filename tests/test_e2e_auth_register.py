from fastapi import status
from typing import Optional


from unittest.mock import Mock, AsyncMock, MagicMock
import pytest
import json

from src.models.users import UserModel
from src.schemas.users import UserSchema
from tests.conftest import TestingSessionLocal, test_user, unconfirmed_user_data, TestClient
from src.conf.messages import ACCOUNT_EXIST
from pathlib import Path
from src.services.auth import auth_service



user_data = {
    "username": "string",
    "email": "user@example.com",
    "password": "string",
}


def test_create_user(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.EmailService.send_varification_mail", mock_send_email)
    response = client.post(
        "/api/auth/register",
        json=user_data,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data['username'] == user_data['username']
    assert data['email'] == user_data['email']
    assert data['avatar'] is None
    assert data['role'] == 'users'
    # assert data['confirmed'] is False
    # assert data['is_active'] is True


@pytest.mark.asyncio
async def test_existing_user_registration(client, monkeypatch):
    # Given an existing user in the system
    existing_user_data = {
        "username": "existing_user",
        "email": "existing@example.com",
        "password": "existing_password",
    }

    # Monkeypatch the necessary functions
    monkeypatch.setattr(auth_service, "create_user", AsyncMock(return_value=None))

    # When trying to register a user with the same username and email
    new_user_data = {
        "username": "existing_user",  # Username already exists
        "email": "existing@example.com",  # Email already exists
        "password": "new_password",
    }

    response = client.post("/api/auth/register", data=new_user_data)











@pytest.mark.asyncio
async def test_register_invalid_data(client, monkeypatch):
    # Invalid data without username
    invalid_user_data = {
        "email": "test@example.com",
        "password": "testpassword",
    }

    # Monkeypatch the necessary functions
    mock_create_user = AsyncMock()
    monkeypatch.setattr(auth_service, "create_user", mock_create_user)

    # Try to register with invalid data
    response = client.post("/api/auth/register", json=invalid_user_data)

    # Then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_data = response.json()
    assert response_data["detail"][0]["msg"].lower() == "field required"

    # Ensure the necessary function was not called
    assert not mock_create_user.called