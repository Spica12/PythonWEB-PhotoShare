from dotenv import load_dotenv
import os

import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from main import app
from src.models.photos import PhotoModel, TransformedImageLinkModel, CommentModel, TagModel
from src.dependencies.database import get_db
from src.models.base import Base
from src.models.users import Roles, UserModel
from src.services.auth import auth_service

# ------------------------------------------------------------------------------------
# TODO : use docker
# ------------------------------------------------------------------------------------
# docker run --name pythoweb-photoshare -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
# docker exec -it pythoweb-photoshare bash
# psql -U postgres
# CREATE DATABASE test;
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
# TODO : Check with pytest-cov
# ------------------------------------------------------------------------------------
#    HTML
# pytest -v --cov=./src tests/ --cov-report html tests/
#
#    Terminal
# pytest -vs --cov-report term --cov=./src tests/
# ------------------------------------------------------------------------------------


load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DB_URL")

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "conf_test",
    "email": "conf_user@example.com",
    "password": "conf_testpassword",
    "avatar": "conf_testavatar",
    "role": "admin",
    "confirmed": True,
    "is_active": True,
}


@pytest.fixture(scope="module", autouse=True)
def init_moduls_wrap():
    async def init_moduls():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            copy_test_user = test_user.copy()
            copy_test_user["password"] = hash_password

            current_user = UserModel(**copy_test_user)
            session.add(current_user)
            await session.commit()

    asyncio.run(init_moduls())


@pytest.fixture(scope="module")
def client():
    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as e:
            print(e)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client


@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(test_user["email"])
    return token


blocked_user = {
    "username": "blocked_user",
    "email": "blocked_user@example.com",
    "password": "test_testpassword",
    "confirmed": True,
    "is_active": False,
    "role": "users",
}

unconfirmed_user_data = {
    "username": "unconfirmed_user",
    "email": "unconfirmed_user@example.com",
    "password": "test_testpassword",
    "confirmed": False,
    "is_active": True,
    "role": "users",
}

confirmed_user_data = {
    "username": "confirmed_user",
    "email": "confirmed_user@example.com",
    "password": "test_testpassword",
    "confirmed": True,
    "is_active": True,
    "role": "users",
}

moderator_data = {
    "username": "moderator_user",
    "email": "moderator_user@example.com",
    "password": "test_testpassword",
    "confirmed": True,
    "is_active": True,
    "role": "moderator",
}


@pytest.fixture()
def create_blocked_user():
    async def _create_blocked_user():
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(blocked_user["password"])
            copy_blocked_user = blocked_user.copy()
            copy_blocked_user["password"] = hash_password

            current_user = UserModel(**copy_blocked_user)
            session.add(current_user)
            await session.commit()

    asyncio.run(_create_blocked_user())


@pytest.fixture()
def create_unconfirmed_user():
    async def _create_unconfirmed_user():
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(
                unconfirmed_user_data["password"]
            )
            copy_unconfirmed_user_data = unconfirmed_user_data.copy()
            copy_unconfirmed_user_data["password"] = hash_password

            current_user = UserModel(**copy_unconfirmed_user_data)
            session.add(current_user)
            await session.commit()

    asyncio.run(_create_unconfirmed_user())


@pytest.fixture()
def create_confirmed_user():
    async def _create_confirmed_user():
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(
                confirmed_user_data["password"]
            )
            copy_confirmed_user_data = confirmed_user_data.copy()
            copy_confirmed_user_data["password"] = hash_password

            current_user = UserModel(**copy_confirmed_user_data)
            session.add(current_user)
            await session.commit()

    asyncio.run(_create_confirmed_user())


@pytest.fixture()
def create_moderator():

    async def _create_moderator():
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(moderator_data["password"])
            moderator_data = moderator_data.copy()
            moderator_data["password"] = hash_password
            current_user = UserModel(**moderator_data)
            session.add(current_user)
            await session.commit()

    asyncio.run(_create_moderator())


async def create_test_photo(username: str):
    async with TestingSessionLocal() as session:
        result = await session.execute(select(UserModel).filter_by(username=username))
        current_user = result.scalar_one_or_none()
        photo = PhotoModel(
            user_id=current_user.id,
            description="test_description",
            image_url="test_url",
            public_id="test_public_id",
        )
        session.add(photo)
        await session.commit()
        await session.refresh(photo)
    return photo


async def create_transform_test_photo(photo_id: int):
    async with TestingSessionLocal() as session:
        result = await session.execute(select(PhotoModel).filter_by(id=photo_id))
        exist_photo = result.scalars().first()
        transform_photo = TransformedImageLinkModel(
            photo_id=exist_photo.id,
            image_url="test_url",
        )
        session.add(transform_photo)
        await session.commit()
        await session.refresh(transform_photo)
    return transform_photo


async def create_test_comment(photo_id: int, username: str):
    async with TestingSessionLocal() as session:
        result = await session.execute(select(PhotoModel).filter_by(id=photo_id))
        exist_photo = result.scalars().first()

        result = await session.execute(select(UserModel).filter_by(username=username))
        user = result.scalar_one_or_none()

        comment = CommentModel(
            content = "test_content",
            photo_id=exist_photo.id,
            user_id= user.id
        )
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
    return comment


async def get_user_id_by_username(username: str):
    async with TestingSessionLocal() as session:
        result = await session.execute(select(UserModel).filter_by(username=username))
        user = result.scalar_one_or_none()
        return user.id


async def create_user_test(
        username: str,
        email: str,
        password: str,
        is_active: bool = True,
        confirmed: bool = True,
        role: Roles = Roles.users
):
    async with TestingSessionLocal() as session:
        hash_password = auth_service.get_password_hash(password)
        copy_confirmed_user_data = confirmed_user_data.copy()

        current_user = UserModel(
            username=username,
            email=email,
            password=hash_password,
            confirmed=confirmed,
            is_active=is_active,
            role=role
        )
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)
        return current_user


async def create_transform_photo(photo_id: int):
    async with TestingSessionLocal() as session:
        transform_photo = TransformedImageLinkModel(
            photo_id=photo_id,
            image_url="http://localhost:8000",
        )
        session.add(transform_photo)
        await session.commit()
        await session.refresh(transform_photo)

    return transform_photo
