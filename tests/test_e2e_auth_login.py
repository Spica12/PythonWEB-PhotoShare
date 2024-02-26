import json
import pytest
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm


# Перевірка для неправильних даних
def test_login_invalid_credentials(client):
    user_data = OAuth2PasswordRequestForm(username="invalid_user@example.com", password="invalid_password")
    response = client.post("/api/auth/login", data={"username": user_data.username, "password": user_data.password})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_unconfirmed_email(client):
    user_data = OAuth2PasswordRequestForm(username="unconfirmed_user@example.com", password="test_testpassword")
    response = client.post("/api/auth/login", data={"username": user_data.username, "password": user_data.password})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Перевірка для заблокованого облікового запису
def test_login_blocked_account(client):
    user_data = OAuth2PasswordRequestForm(username="blocked_user@example.com", password="blocked_user")
    response = client.post("/api/auth/login", data={"username": user_data.username, "password": user_data.password})

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        # User is not found or invalid username/password
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif response.status_code == status.HTTP_403_FORBIDDEN:
        # User is blocked
        assert response.status_code == status.HTTP_403_FORBIDDEN
    else:
        # Unexpected response status code
        assert False, f"Unexpected response status code: {response.status_code}"


def test_login_valid_account(client):
    user_data = OAuth2PasswordRequestForm(username="conf_user@example.com", password="conf_testpassword")

    response = client.post("/api/auth/login", data={"username": user_data.username, "password": user_data.password})
    print(response.json())
    # Перевірка відповіді сервера
    assert response.status_code == status.HTTP_200_OK, f"Статус код відповіді не є 200: {response.status_code}"
    data = response.json()
    assert "access_token" in data, "Токен доступу відсутній у відповіді"
    assert "refresh_token" in data, "Токен оновлення відсутній у відповіді"
    assert data["token_type"] == "bearer", f"Неправильний тип токена: {data['token_type']}"
