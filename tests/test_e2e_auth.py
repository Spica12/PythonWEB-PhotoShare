from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import select


user_data = {
    "username": "string",
    "email": "user@example.com",
    "password": "string",
}


def test_signup(client, monkeypatch):
    mock_send_varification_email = Mock()
    monkeypatch.setattr(
        "src.services.email.EmailService.send_varification_mail",
        mock_send_varification_email,
    )
    response = client.post("api/auth/register", json=user_data)

    assert response.status_code == 201, response.text
    assert mock_send_varification_email.called
    data = response.json()

    assert data['username'] == user_data['username']
    assert data['email'] == user_data['email']
    assert data['avatar'] is None
    assert data['role'] == 'users'
    # assert data['confirmed'] is False
    # assert data['is_active'] is True
