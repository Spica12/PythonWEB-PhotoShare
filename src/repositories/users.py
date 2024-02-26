from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

# models
from src.models.users import BlackListModel, Roles, TokenModel, UserModel

# schemas
from src.schemas.users import UserSchema


class UserRepo:
    def __init__(self, db):
        self.db: AsyncSession = db

    async def get_user_by_username(self, username: str):
        stmt = select(UserModel).filter_by(username=username)
        user = await self.db.execute(stmt)
        user = user.scalar_one_or_none()
        return user

    async def get_user_by_id(self, user_id: UUID):
        stmt = select(UserModel).filter_by(id=user_id)
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
        new_user = UserModel(**body.model_dump(), avatar=None)
        # Check if users exist
        if not users:
            new_user.confirmed = True
            new_user.role = Roles.admin
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def change_email(self, user_id: UUID, new_email: str):
        stmt = select(UserModel).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        user = user.scalar_one_or_none()
        user.email = new_email
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_refresh_token_by_user(self, user: UserModel):
        stmt = select(TokenModel).filter_by(user_id=user.id)
        token = await self.db.execute(stmt)
        token = token.scalar_one_or_none()
        return token

    async def update_password(self, user_id: UUID, new_password_hash: str):
        stmt = select(UserModel).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        user = user.scalar_one_or_none()
        user.password = new_password_hash
        await self.db.commit()
        await self.db.refresh(user)

    async def update_refresh_token(
        self, user: UserModel, refresh_token: TokenModel | None
    ):
        stmt = select(TokenModel).filter_by(user_id=user.id)
        token = await self.db.execute(stmt)
        token = token.scalar_one_or_none()
        if token:
            token.token = refresh_token
        else:
            new_token = TokenModel(token=refresh_token, user_id=user.id)
            self.db.add(new_token)
        await self.db.commit()

    async def remove_refresh_token(self, user: UserModel):
        stmt = select(TokenModel).filter_by(user_id=user.id)
        result = await self.db.execute(stmt)
        result = result.scalar_one_or_none()
        if result:
            await self.db.delete(result)
            await self.db.commit()
        return result

    async def add_token_to_blacklist(self, token: str):
        # add access token to blacklist when user banned or use @logout
        new_token = BlackListModel(token=token)
        self.db.add(new_token)
        await self.db.commit()
        await self.db.refresh(new_token)
        return new_token

    async def get_token_blacklist(self, token: str):
        # to check if object exists (token in blacklist)
        stmt = select(BlackListModel).filter_by(token=token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def confirmed_email(self, user: UserModel) -> None:
        user.confirmed = True
        await self.db.commit()

    async def update_avatar(self, user_id: UUID, avatar_url: str) -> UserModel:
        stmt = select(UserModel).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        user = user.scalar_one_or_none()
        user.avatar = avatar_url
        await self.db.commit()
        await self.db.refresh(user)
        return user
