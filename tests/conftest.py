import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from main import app
from src.models.base import Base
from src.models.users import UserModel

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False,)

test_user = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword"
}



@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with TestingSessionLocal() as session:
            #TODO Change on service get_hash_password
            hash_password = test_user["password"]
            current_user = UserModel(
                username=test_user["username"],
                email=test_user["email"],
                password_hash=hash_password,
                confirmed=True,
            )
            session.add(UserModel(**test_user))
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())
