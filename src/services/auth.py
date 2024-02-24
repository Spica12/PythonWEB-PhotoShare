from copy import copy
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models.users import UserModel
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

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=messages.COULD_NOT_VALIDATE_CREDENTIALS,
        headers={"WWW-AUTHENTICATE": "BEARER"},
    )

    async def get_user_by_id(self, user_id: UUID, db: AsyncSession):
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

    async def check_access_token_blacklist(self, token, db: AsyncSession):
        blacklist = await UserRepo(db).get_token_blacklist(token)
        return blacklist

    async def extract_token_data(self, token, db: AsyncSession):
        # double usage of code, separate func
        # check if we can use token (not in blacklist)
        # if it is - raise 401.
        blacklist = await self.check_access_token_blacklist(token, db)
        if blacklist is not None:
            raise self.credentials_exception

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            if payload["scope"] == "access_token":
                if email is None:
                    raise self.credentials_exception
            else:
                raise self.credentials_exception
        except JWTError:
            raise self.credentials_exception
        user_hash = str(email)
        user = await UserRepo(db).get_user_by_email(user_hash)
        if user is None:
            raise self.credentials_exception
        return user

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        need add to routers:

        from src.models.users import UserModel
        from src.services.auth import auth_service

        user: UserModel = Depends(auth_service.get_current_user)
        """
        # if token not in blacklist and user exists - extract and return current user
        user = await self.extract_token_data(token, db)
        return user

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

    async def get_refresh_token_by_user(self, user: UserModel, db: AsyncSession):
        refresh_token = await UserRepo(db).get_refresh_token_by_user(user)
        return refresh_token

    async def update_refresh_token(self, user: UserModel, refresh_token: str | None, db: AsyncSession):
        await UserRepo(db).update_refresh_token(user, refresh_token)

    async def add_token_to_blacklist(self, token: str, db: AsyncSession):
        await UserRepo(db).add_token_to_blacklist(token)

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=messages.INVALID_TOKEN)

    async def confirmed_email(self, user: UserModel, db: AsyncSession):
        await UserRepo(db).confirmed_email(user)

    async def logout_service(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        # extract user from token
        # if we have no user
        # using copy because of sqlalchemy rewrite some data in previous objects
        user = copy(await self.extract_token_data(token, db))

        # clear refresh token data for current user
        await UserRepo(db).remove_refresh_token(user)

        # adding access token to blacklist
        await self.add_token_to_blacklist(token=token, db=db)
        return "logout"


auth_service = AuthService()
