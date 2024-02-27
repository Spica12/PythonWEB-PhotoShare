from dotenv import load_dotenv
import os

import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from main import app
from src.dependencies.database import get_db
from src.models.base import Base
from src.models.users import UserModel
from src.services.auth import auth_service

# ------------------------------------------------------------------------------------
# TODO : use docker
# ------------------------------------------------------------------------------------
# docker run --name pythoweb-photoshare -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
# docker exec -it pythoweb-photoshare bash
# psql -U postgres
# CREATE DATABASE test;
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
    'role': 'admin',
    'confirmed': True,
    'is_active': True
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
        "username": "blocked_user@example.com",
        "email": "blocked_user@example.com",
        "password": "test_testpassword",
        "confirmed": True,
        "is_active": False,
        "role": "users",
    }

unconfirmed_user_data = {
    "username": "unconfirmed_user@example.com",
    "email": "unconfirmed_user@example.com",
    "password": "test_testpassword",
    "confirmed": False,
    "is_active": True,
    "role": "users",
}

confirmed_user_data = {
    "username": "confirmed_user@example.com",
    "email": "confirmed_user@example.com",
    "password": "test_testpassword",
    "confirmed": True,
    "is_active": True,
    "role": "users",
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
            hash_password = auth_service.get_password_hash(unconfirmed_user_data["password"])
            copy_unconfirmed_user_data = unconfirmed_user_data.copy()
            copy_unconfirmed_user_data["password"] = hash_password

            current_user = UserModel(**copy_unconfirmed_user_data)
            session.add(current_user)
            await session.commit()

    asyncio.run(_create_unconfirmed_user())


@pytest.fixture()
def create_confirmed_user(name="confirmed_user"):
    async def _create_confirmed_user():
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(confirmed_user_data["password"])
            copy_confirmed_user_data = confirmed_user_data.copy()
            copy_confirmed_user_data["password"] = hash_password

            current_user = UserModel(**copy_confirmed_user_data)
            session.add(current_user)
            await session.commit()

    asyncio.run(_create_confirmed_user())
