from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
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

    async def reset_password_and_notify_user(self, email: str, db: AsyncSession):
        user = await self.get_user_by_email(email, db)

        if user:
            new_password = self.generate_random_password()
            hashed_password = self.get_password_hash(new_password)

            try:
                # Update user's password in the database
                await self.update_user_password(user.id, hashed_password, db)

                # Send password reset notification
                await self.send_password_reset_notification(email, new_password)
            except Exception as e:
                print(f"Error resetting password and notifying user: {e}")
        else:
            print(f"User with email {email} not found.")

    async def send_password_reset_notification(self, email, new_password):
        try:
            # Generate a new password reset token
            token_reset = auth_service.create_email_token({"sub": email})

            # Prepare the email message
            message = MessageSchema(
                subject="Password Reset",
                recipients=[email],
                template_body={"new_password": new_password, "token_reset": token_reset},
                subtype=MessageType.html
            )

            # Send the email using EmailService
            await EmailService().fm.send_message(message, template_name="password_reset_email.html")

        except ConnectionErrors as err:
            print(err)

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
