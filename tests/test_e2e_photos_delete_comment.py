import pytest
from copy import copy, deepcopy
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from src.models.users import Roles
from src.models.photos import CommentModel, PhotoModel, TransformedImageLinkModel
from fastapi import status

from tests.conftest import (
    TestingSessionLocal,
    confirmed_user_data,
    moderator_data,
    create_test_photo,
    create_transform_test_photo,
    get_user_id_by_username,
    create_test_comment,
    create_user_test,
)
from src.services.auth import auth_service
from src.conf import messages


from conftest import test_user


@pytest.mark.asyncio
async def test_delete_photo_comment(client, get_token):
    photo = await create_test_photo(test_user["username"])
    comment = await create_test_comment(photo.id, test_user["username"])
    assert comment is not None

    response = client.delete(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {get_token}"},
        params={"select": "comment", "object_id": comment.id},
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(select(CommentModel).filter_by(id=comment.id))
        comment = result.scalar_one_or_none()
        assert comment is None

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_photo_comment_not_found(client, get_token):
    photo = await create_test_photo(test_user["username"])

    response = client.delete(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {get_token}"},
        params={"select": "comment", "object_id": 1},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_photo_comment_by_owner(client, get_token):
    """
    Owner can not delete comments
    """
    user = {
        "username": "test_tesdfgt_user",
        "email": "test_usedfgdfgr_user@example.com",
        "password": "password",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }

    user = await create_user_test(**user)
    photo = await create_test_photo(user.username)
    comment = await create_test_comment(photo.id, user.username)
    assert comment is not None

    user_token = await auth_service.create_access_token(user.email)

    response = client.delete(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"select": "comment", "object_id": comment.id},
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(select(CommentModel).filter_by(id=comment.id))
        comment = result.scalar_one_or_none()
        assert comment is not None

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_photo_comment_by_moderator(client):
    """
    Moderator can delete comments
    """
    moderator = {
        "username": 'test_moderator22',
        "email": 'test_moderator22@example.com',
        "password": 'password',
        "is_active": True,
        "confirmed": True,
        "role": Roles.moderator,
    }
    user = {
        "username": 'test_test_user',
        "email": 'test_user_user@example.com',
        "password": 'password',
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }

    user = await create_user_test(**user)
    moderator = await create_user_test(**moderator)
    photo = await create_test_photo(user.username)
    comment = await create_test_comment(photo.id, user.username)
    assert comment is not None

    moderator_token = await auth_service.create_access_token(moderator.email)

    response = client.delete(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {moderator_token}"},
        params={"select": "comment", "object_id": comment.id},
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(select(CommentModel).filter_by(id=comment.id))
        comment = result.scalar_one_or_none()
        assert comment is None

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_photo_comment_by_admin(client, get_token):
    """
    Owner can not delete comments
    """
    admin = {
        "username": 'test_admin',
        "email": 'test_admin@example.com',
        "password": 'password',
        "is_active": True,
        "confirmed": True,
        "role": Roles.admin,
    }
    user = {
        "username": 'test_user_test',
        "email": 'test_user@example.com',
        "password": 'password',
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }

    user = await create_user_test(**user)
    admin = await create_user_test(**admin)
    photo = await create_test_photo(admin.username)
    comment = await create_test_comment(photo.id, user.username)
    assert comment is not None

    response = client.delete(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {get_token}"},
        params={"select": "comment", "object_id": comment.id},
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(select(CommentModel).filter_by(id=comment.id))
        comment = result.scalar_one_or_none()
        assert comment is None

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_photo_comment_by_unknown(client, get_token):
    """
    Owner can not delete comments
    """
    user1 = {
        "username": "test_user1",
        "email": "test_user1@example.com",
        "password": "password",
        "is_active": True,
        "confirmed": True,
        "role": Roles.admin,
    }

    user1 = await create_user_test(**user1)
    photo = await create_test_photo(user1.username)
    comment = await create_test_comment(photo.id, user1.username)

    response = client.delete(
        f"api/photos/{photo.id}",
        params={"select": "comment", "object_id": comment.id},
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(select(CommentModel).filter_by(id=comment.id))
        comment = result.scalar_one_or_none()
        assert comment is not None

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
