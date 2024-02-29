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
async def test_get_photo_by_unknown(client):
    user_data = {
        "username": "teasfdsdfst",
        "email": "tessdfsdft@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)

    response = client.get(f"api/photos/{photo.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == user.username


@pytest.mark.asyncio
async def test_get_photo_not_found(client):

    response = client.get(f"api/photos/{666}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_photo_by_unknown(client):
    user_data = {
        "username": "ihui",
        "email": "jjhjk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)

    content = "New description of the photo"


    response = client.put(
        f"api/photos/{photo.id}",
        params={
            "content": content,
            "select": "photo",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_photo_not_found_by_user(client):
    user_data = {
        "username": "ihasui",
        "email": "jjhjsdk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    user_token = await auth_service.create_access_token(user.email)

    content = "New description of the photo"

    response = client.put(
        f"api/photos/{666}",
        headers={"Authorization": f"Bearer {user_token}"},
        params={
            "content": content,
            "select": "photo",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_photo_by_user(client):
    user_data = {
        "username": "ihasdfgui",
        "email": "jjhfgggjsdk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)
    user_token = await auth_service.create_access_token(user.email)

    content = "New description of the photo"

    response = client.put(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        params={
            "content": content,
            "select": "photo",
        },
    )
    async with TestingSessionLocal() as session:
        exist_photo = await session.get(PhotoModel, photo.id)
        assert exist_photo is not None
        assert exist_photo.description == content

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_photo_by_moderator(client):
    user_data = {
        "username": "ihasdfguassadasdi",
        "email": "jjhfhhgggjsssdk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    moderator_data = {
        "username": "ihasasdasdfguidd",
        "email": "jjhfggddddhhhhgjsdk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.moderator,
    }
    user = await create_user_test(**user_data)
    moderator = await create_user_test(**moderator_data)
    photo = await create_test_photo(user.username)
    moderator_token = await auth_service.create_access_token(moderator.email)

    content = "New description of the photo"

    response = client.put(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {moderator_token}"},
        params={
            "content": content,
            "select": "photo",
        },
    )
    async with TestingSessionLocal() as session:
        exist_photo = await session.get(PhotoModel, photo.id)
        assert exist_photo is not None
        assert exist_photo.description == content

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_photo_by_admin(client):
    user_data = {
        "username": "ihasdfguassadasdi1",
        "email": "jjhfhhgggjsssdwk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    admin_data = {
        "username": "ihasasssdasdfguidd1",
        "email": "jjhfggddddddhhhhgjsdks@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.admin,
    }
    user = await create_user_test(**user_data)
    admin = await create_user_test(**admin_data)
    photo = await create_test_photo(user.username)
    admin_token = await auth_service.create_access_token(admin.email)

    content = "New description of the photo"

    response = client.put(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={
            "content": content,
            "select": "photo",
        },
    )
    async with TestingSessionLocal() as session:
        exist_photo = await session.get(PhotoModel, photo.id)
        assert exist_photo is not None
        assert exist_photo.description == content

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_photo_by_another_user(client):
    user_data = {
        "username": "ihasssdfguassadasdi1",
        "email": "jjhddfhhgggjsssdwk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    another_user_data = {
        "username": "ihasssasssdasdfguidd1",
        "email": "jjhfggdffdddddhhhhgjsdks@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    another_user = await create_user_test(**another_user_data)
    photo = await create_test_photo(user.username)
    another_user_token = await auth_service.create_access_token(another_user.email)

    content = "New description of the photo"
    assert photo.user_id != another_user.id
    response = client.put(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {another_user_token}"},
        params={
            "content": content,
            "select": "photo",
        },
    )
    async with TestingSessionLocal() as session:
        exist_photo = await session.get(PhotoModel, photo.id)
        assert exist_photo is not None
        assert exist_photo.id == photo.id
        assert exist_photo.description == photo.description

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_update_photo_comment_by_unknown(client):
    user_data = {
        "username": "ihussi",
        "email": "jjhnmnjk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)
    comment = await create_test_comment(photo.id, user.username)

    content = "New comment"

    response = client.put(
        f"api/photos/{photo.id}",
        params={
            "content": content,
            "select": "comment",
            'object_id': comment.id,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_photo_comment_not_found_by_user(client):
    user_data = {
        "username": "ihsssui",
        "email": "jjhjsdddk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)
    user_token = await auth_service.create_access_token(user.email)

    content = "New comment"

    response = client.put(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        params={
            "content": content,
            "select": "comment",
            "object_id": 666,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == messages.COMMENT_NOT_FOUND


@pytest.mark.asyncio
async def test_update_photo_comment_by_user(client):
    user_data = {
        "username": "ihasdfgussi",
        "email": "jjhfgggjddsdk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    photo = await create_test_photo(user.username)
    comment = await create_test_comment(photo.id, user.username)

    user_token = await auth_service.create_access_token(user.email)

    content = "New comment"

    response = client.put(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        params={
            "content": content,
            "select": "comment",
            "object_id": comment.id,
        },
    )
    async with TestingSessionLocal() as session:
        exist_comment = await session.get(CommentModel, comment.id)
        assert exist_comment is not None
        assert exist_comment.id == comment.id
        assert exist_comment.content == content

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_photo_comment_by_moderator(client):
    user_data = {
        "username": "ihasdfgussssi",
        "email": "jjhfgggjddsdddk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    moderator_data = {
        "username": "ihasdfgussssddi",
        "email": "jjhfgggjddsdddddk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.moderator,
    }
    user = await create_user_test(**user_data)
    moderator = await create_user_test(**moderator_data)
    photo = await create_test_photo(user.username)
    comment = await create_test_comment(photo.id, user.username)

    moderator_token = await auth_service.create_access_token(moderator.email)

    content = "New comment"

    response = client.put(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {moderator_token}"},
        params={
            "content": content,
            "select": "comment",
            "object_id": comment.id,
        },
    )
    async with TestingSessionLocal() as session:
        exist_comment = await session.get(CommentModel, comment.id)
        assert exist_comment is not None
        assert exist_comment.id == comment.id
        assert exist_comment.content == content

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_photo_comment_by_admin(client):
    user_data = {
        "username": "ihasdfgu3ssssi",
        "email": "jjhfgggjddsdddaak@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    admin_data = {
        "username": "ihasdf3gussssssddi",
        "email": "jjhfggssgjddsdssddddk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.admin,
    }
    user = await create_user_test(**user_data)
    admin = await create_user_test(**admin_data)
    photo = await create_test_photo(user.username)
    comment = await create_test_comment(photo.id, user.username)

    moderator_token = await auth_service.create_access_token(admin.email)

    content = "New comment"

    response = client.put(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {moderator_token}"},
        params={
            "content": content,
            "select": "comment",
            "object_id": comment.id,
        },
    )
    async with TestingSessionLocal() as session:
        exist_comment = await session.get(CommentModel, comment.id)
        assert exist_comment is not None
        assert exist_comment.id == comment.id
        assert exist_comment.content == content

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_photo_comment_by_another_user(client):
    user_data = {
        "username": "ih3asdfgu3ssssi",
        "email": "jjh4fgggjddsdddaak@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    another_user_data = {
        "username": "i2hasdf3gussssssddi",
        "email": "jjhf2ggssgjddsdssddddk@mail.com",
        "password": "test",
        "is_active": True,
        "confirmed": True,
        "role": Roles.users,
    }
    user = await create_user_test(**user_data)
    another_user = await create_user_test(**another_user_data)
    photo = await create_test_photo(user.username)
    comment = await create_test_comment(photo.id, user.username)

    another_user_token = await auth_service.create_access_token(another_user.email)

    content = "New comment"

    response = client.put(
        f"api/photos/{photo.id}",
        headers={"Authorization": f"Bearer {another_user_token}"},
        params={
            "content": content,
            "select": "comment",
            "object_id": comment.id,
        },
    )
    async with TestingSessionLocal() as session:
        exist_comment = await session.get(CommentModel, comment.id)
        assert exist_comment is not None
        assert exist_comment.id == comment.id
        assert exist_comment.content == comment.content

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()['detail'] == messages.NO_EDIT_RIGHTS
