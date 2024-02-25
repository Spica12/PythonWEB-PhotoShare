from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import select
from src.models.users import UserModel
from tests.conftest import TestingSessionLocal, test_user
from src.conf import messages


user_data = {
    "username": "string",
    "email": "user@example.com",
    "password": "string",
}


@pytest.mark.asyncio
async def test_get_current_user_not_authenticated(client):
    response = client.get("api/users/my_profile")
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_AUTHENTICATED


@pytest.mark.asyncio
async def test_get_current_user(client, get_token):

    response = client.get("api/users/my_profile", headers={"Authorization": f"Bearer {get_token}"} )

    assert response.status_code == 200 , response.text
    data = response.json()
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%', data)
    assert data['username'] == test_user['username']
    assert data['email'] == test_user['email']
    assert data['avatar'] is None
    assert data['role'] == 'users'
    assert data['confirmed'] is False
    assert data['is_active'] is True
