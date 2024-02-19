from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.models.users import TokenModel, UserModel
from src.schemas.users import UserSchema


class UserRepo:
    
    def __init__(self, db):
        self.db: AsyncSession = db

    async def get_user_by_username(self, username: str):
        stmt = select(UserModel).filter_by(username=username)
        user = await self.db.execute(stmt)
        user = user.scalar_one_or_none()

        return user

    async def get_user_by_id(self, user_id: str):
        stmt = select(UserModel).filter_by(user_id=user_id)
        user = await self.db.execute(stmt)
        user = user.scalar_one_or_none()

        return user

    async def get_user_by_email(self, email: str):
        stmt = select(UserModel).filter_by(email=email)
        user = await self.db.execute(stmt)
        user = user.scalar_one_or_none()

        return user

    async def create_user(self, body: UserSchema):
        new_user = UserModel(
            **body.model_dump(), avatar=None
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user
