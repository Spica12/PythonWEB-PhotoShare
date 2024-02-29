import pytest
from copy import copy, deepcopy
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from src.models.users import Roles
from src.models.photos import CommentModel, PhotoModel, RatingModel
from fastapi import status

from tests.conftest import (
    TestingSessionLocal,
    confirmed_user_data,
    moderator_data,
    create_test_photo,
    create_user_test,
)
from src.services.auth import auth_service
from src.conf import messages

from conftest import test_user


@pytest.mark.asyncio
async def test_add_rate_authenticated_user(client, get_token):
    # Create user
    user = {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "password",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user)

    # Upload photo
    photo = await create_test_photo(user.username)

    # Create another user
    other_user = {
        "username": "other_user",
        "email": "other_user@example.com",
        "password": "password",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    other_user = await create_user_test(**other_user)

    # Generate token for the other user
    other_user_token = await auth_service.create_access_token(other_user.email)

    # Add rating
    rating = 3  # Rating from 1 to 5
    response = client.post(
        f"api/photos/{photo.id}/set-rate",
        headers={"Authorization": f"Bearer {other_user_token}"},
        json={"rate": rating},
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_add_rate_unauthenticated_user(client, get_token):
    # Create user
    super_user = {
        "username": "super_user",
        "email": "super_user@example.com",
        "password": "password",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    super_user = await create_user_test(**super_user)

    # Upload photo
    photo = await create_test_photo(super_user.username)

    unconfirmed_user = {
        "username": "unconfirmed_user",
        "email": "unconfirmed_user@example.com",
        "password": "password",
        "is_active": True,
        "confirmed": False,
        "role": Roles.users,
    }
    unconfirmed_user = await create_user_test(**unconfirmed_user)

    # Add rating as unconfirmed user
    rating = 3  # Rating from 1 to 5
    response = client.post(
        f"api/photos/{photo.id}/set-rate",
        json={"rate": rating},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_add_rate_not_found_photo(client, get_token, monkeypatch):
    photo = await create_test_photo(test_user["username"])
    photo_id = 999
    rate_value = 5

    response = client.post(
        f"/photos/{photo_id + 1}/set-rate",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"value": rate_value}
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(select(RatingModel).filter_by(photo_id=photo_id))
        rate = result.scalar_one_or_none()
        assert rate is None

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_add_rate_photo_owner(client, get_token):
    # Create user
    mega_user = {
        "username": "mega_user",
        "email": "mega_user@example.com",
        "password": "password",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    mega_user = await create_user_test(**mega_user)

    # Upload photo
    photo = await create_test_photo(mega_user.username)

    mega_user_token = await auth_service.create_access_token(mega_user.email)

    # Add rating
    rating = 3  # Rating from 1 to 5
    response = client.post(
        f"api/photos/{photo.id}/set-rate",
        headers={"Authorization": f"Bearer {mega_user_token}"},
        json={"rate": rating},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.fixture
async def clean_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.mark.asyncio
async def test_add_rate_photo_with_wrong_value(client, get_token):
    # Create user
    big_user = {
        "username": "big_user",
        "email": "big_user@example.com",
        "password": "password",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    big_user = await create_user_test(**big_user)

    # Upload photo
    photo = await create_test_photo(big_user.username)

    # Create another user
    last_user = {
        "username": "last_user",
        "email": "last_user@example.com",
        "password": "password",
        "is_active": True,
        "confirmed": True,
        "role": Roles.moderator,
    }
    last_user = await create_user_test(**last_user)

    # Generate token for the other user
    last_user_token = await auth_service.create_access_token(last_user.email)

    # Add rating
    rating = 7  # Rating from 1 to 5
    response = client.post(
        f"api/photos/{photo.id}/set-rate",
        headers={"Authorization": f"Bearer {last_user_token}"},
        json={"rate": rating},
    )

    assert response.status_code == status.HTTP_201_CREATED
