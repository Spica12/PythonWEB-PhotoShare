from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.models.users import BlackListModel, Roles, TokenModel, UserModel
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
        # Get all exist users in db
        stmt = select(UserModel)
        users = await self.db.execute(stmt)
        users = users.scalars().all()
        # Create new user
        new_user = UserModel(
            **body.model_dump(), avatar=None
        )
        # Check if users exist
        if not users:
            new_user.confirmed = True
            new_user.role = Roles.admin
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def update_refresh_token(self, user: UserModel, refresh_token: TokenModel | None):
        stmt = select(TokenModel).filter_by(user_id=user.id)
        token = await self.db.execute(stmt)
        token = token.scalar_one_or_none()
        if token:
            token.token = refresh_token
        else:
            new_token = TokenModel(token=refresh_token, user_id=user.id)
            self.db.add(new_token)
        await self.db.commit()

    async def add_token_to_blacklist(self, token: str):
        new_token = BlackListModel(token=token)
        self.db.add(new_token)
        await self.db.commit()
