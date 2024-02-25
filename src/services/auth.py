from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    async def add_token_to_blacklist(self, user: UserModel, token: str, db: AsyncSession):
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

    def generate_random_password(self):
        # Генерація рандомного пароля
        length = 12
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(secrets.choice(alphabet) for i in range(length))

    async def reset_password_and_notify_user(
            self, email: str, username: str, new_password: str, db: AsyncSession
    ):
        # Check if the user exists by email or username
        user = await UserRepo(db).get_user_by_email_and_username(email, username)
        if user:
            hashed_password = self.get_password_hash(new_password)

            # Update user's password in the database
            await UserRepo(db).update_user_password(user.id, hashed_password)

            print("Password reset successfully.")
        else:
            print(f"User with email {email} or username {username} not found.")

        # Check if the user exists by username
        user_by_username = await UserRepo(db).get_user_by_username(username)
        if user_by_username:
            # Update user's password by username in the database
            await UserRepo(db).update_user_password(user_by_username.id, hashed_password)
        else:
            print(f"User with username {username} not found.")

    async def get_user_by_email_and_username(self, email: str, username: str, db: AsyncSession):
        stmt = select(UserModel).filter(
            (UserModel.email == email) & (UserModel.username == username)
        )
        user = await db.execute(stmt)
        user = user.scalar_one_or_none()
        return user

    async def update_user_password(self, user_id: UUID, new_password: str, db: AsyncSession):
        user = await self.get_user_by_id(user_id, db)
        if user:
            try:
                hashed_password = self.get_password_hash(new_password)
                user.password = hashed_password
                user_repo = UserRepo(db)

                await user_repo.update_user(user)
            except Exception as e:
                print(f"Error updating user password: {e}")
        else:
            print(f"User with ID {user_id} not found.")


auth_service = AuthService()
