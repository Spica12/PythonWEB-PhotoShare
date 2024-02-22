from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import UserModel
from src.models.users import BlacklistToken
from src.conf.config import config
from src.conf import messages
from src.dependencies.database import get_db
from src.repositories.users import UserRepo
from src.schemas.users import UserSchema


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    def __init__(self, db: AsyncSession):
        self.repo = UserRepo(db)


    async def get_user_by_id(self, user_id: int, db: AsyncSession):
        user = await UserRepo(db).get_user_by_id(user_id)
        return user

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_pasword):
        return self.pwd_context.verify(plain_password, hashed_pasword)

    async def create_user(self, body: UserSchema, db: AsyncSession):
        new_user = await UserRepo(db).create_user(body)

        return new_user

    async def get_user_by_username(self, username: str, db: AsyncSession):
        user = await UserRepo(db).get_user_by_username(username)
        return user

    async def get_user_by_email(self, email: str, db: AsyncSession):
        user = await UserRepo(db).get_user_by_email(email)
        return user

    # async def get_current_user(self, email: str, db: AsyncSession):
    #     user = await UserRepo(db).get_user_by_email(email)
    #     return user

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.COULD_NOT_VALIDATE_CREDENTIALS,
            headers={"WWW-AUTHENTICATE": "BEARER"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]

            if payload["scope"] == "access_token":
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception

        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)
        user = await UserRepo(db).get_user_by_email(user_hash)
        if user is None:
            raise credentials_exception

        return user
        # to router need add next
        #
        # from src.models.users import UserModel
        # from src.services.auth import auth_service
        #
        # user: UserModel = Depends(auth_service.get_current_user)

    async def create_access_token(self, email: str, expires_delta: Optional[float] = None):
        to_encode = {"sub": str(email)}
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encode_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encode_jwt

    async def create_refresh_token(self, email: str, expires_delta: Optional[float] = None):
        to_encode = {"sub": str(email)}
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encode_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encode_jwt

    async def update_refresh_token(self, user: UserModel, refresh_token: str | None, db: AsyncSession):
        await UserRepo(db).update_refresh_token(user, refresh_token)

    async def add_token_to_blacklist(self, token: str, db: AsyncSession):
        async with db() as session:
            blacklist_token = BlacklistToken(token=token)
            session.add(blacklist_token)
            await session.commit()



auth_service = AuthService()
