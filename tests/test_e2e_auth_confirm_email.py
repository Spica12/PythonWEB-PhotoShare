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
from src.schemas.users import RequestPasswordResetSchema
from pydantic import BaseModel, EmailStr
from src.repositories.users import UserRepo


def test_confirmed_email(client, monkeypatch):
    # Given
    user_email = "user@example.com"
    mock_confirmed_email = MagicMock()
    monkeypatch.setattr(auth_service, "confirmed_email", mock_confirmed_email)

    # Mock the necessary functions for email token creation
    mock_create_email_token = MagicMock(return_value=auth_service.create_email_token({"sub": user_email}))
    monkeypatch.setattr(auth_service, "create_email_token", mock_create_email_token)

    # When
    token_verification = auth_service.create_email_token({"sub": user_email})
    response = client.get(f"/api/auth/confirmed_email/{token_verification}",
                          headers={"Authorization": f"Bearer {token_verification}"})

    # Then
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == messages.VERIFICATION_ERROR

    # Check if the necessary function was called
    mock_confirmed_email.assert_not_called()
    mock_create_email_token.assert_called_once_with({"sub": user_email})