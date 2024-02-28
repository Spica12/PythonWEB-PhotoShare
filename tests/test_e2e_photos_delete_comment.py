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

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_photo_comment_by_owner(client, get_token):
    """
    Owner can not delete comments
    """
    confirmed_user = await create_user_test(
        username = confirmed_user_data["username"],
        email = confirmed_user_data["email"],
        password = confirmed_user_data["password"],
        is_active = confirmed_user_data["is_active"],
        confirmed = confirmed_user_data["confirmed"],
        role = Roles.users
    )
    photo = await create_test_photo(confirmed_user_data["username"])
    comment = await create_test_comment(photo.id, test_user["username"])
    assert comment is not None

    confirmed_user_token = await auth_service.create_access_token(
        confirmed_user.email
    )

    response = client.delete(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {confirmed_user_token}"},
        params={"select": "comment", "object_id": comment.id},
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(select(CommentModel).filter_by(id=comment.id))
        comment = result.scalar_one_or_none()
        assert comment is None

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_photo_comment_by_moderator(client):
    """
    Owner can not delete comments
    """
    moderator = await create_user_test(
        username=moderator_data["username"],
        email=moderator_data["email"],
        password=moderator_data["password"],
        is_active=moderator_data["is_active"],
        confirmed=moderator_data["confirmed"],
        role=Roles.moderator,
    )
    photo = await create_test_photo(confirmed_user_data["username"])
    comment = await create_test_comment(photo.id, test_user["username"])
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
    admin = await get_user_id_by_username(test_user["username"])
    photo = await create_test_photo(confirmed_user_data["username"])
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
async def test_delete_photo_comment_by_unknown(client, get_token):
    """
    Owner can not delete comments
    """
    photo = await create_test_photo(confirmed_user_data["username"])
    comment = await create_test_comment(photo.id, test_user["username"])
    assert comment is not None

    response = client.delete(
        f"api/photos/{photo.id}",
        params={"select": "comment", "object_id": comment.id},
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(select(CommentModel).filter_by(id=comment.id))
        comment = result.scalar_one_or_none()
        assert comment is not None

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
