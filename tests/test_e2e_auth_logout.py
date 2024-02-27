import pytest
from fastapi import status
from starlette.responses import RedirectResponse


def test_logout(client):
    # Отримуємо токен доступу
    response_login = client.post("/api/auth/login",
                                 data={"username": "conf_user@example.com", "password": "conf_testpassword"})
    assert response_login.status_code == status.HTTP_200_OK
    access_token = response_login.json()["access_token"]

    # Додаємо токен доступу до заголовка авторизації
    headers = {"Authorization": f"Bearer {access_token}"}

    # Виконуємо вихід з системи
    response_logout = client.get("/api/auth/logout", headers=headers)

    assert response_logout.status_code == 200

    # Перевіряємо, що після виходу токен доступу став недійсним
    response_access = client.get("/api/auth/profile/access", headers=headers)
    assert response_access.status_code == 401
