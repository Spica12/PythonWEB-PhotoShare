from datetime import datetime
from typing import Optional
import uuid
from fastapi import File, UploadFile
from pydantic import BaseModel, EmailStr, Field, HttpUrl

from src.models.users import Roles


class UserNameSchema(BaseModel):
    username: str


class RequestEmail(BaseModel):
    email: EmailStr


class UserSchema(RequestEmail):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=4, max_length=20)


class UserResponse(RequestEmail, UserNameSchema):
    id: uuid.UUID
    # username: str
    # email: EmailStr
    avatar: str | None
    role: Roles
    # picture_count: Optional[int]
    confirmed: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateEmailSchema(BaseModel):
    # Validation of user input during profile update
    email: EmailStr = Field(max_length=255)
    confirm_password: str = Field(max_length=255)


class UserUpdateAvatarSchema(BaseModel):
    # Validation of user input during profile update
    avatar: UploadFile = File()
    confirm_password: str = Field(max_length=255)


class AnotherUsers(RequestEmail, UserNameSchema):
    # username: str
    # email: EmailStr
    avatar: HttpUrl | None
    role: Roles
    picture_count: Optional[int]
    created_at: datetime


class TokenSchema(BaseModel):
    # не включаю id, якщо його буде автоматично генерувати база даних.
    # id: int
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    # created_at: datetime
    # updated_at: datetime

    # Поки не включаю час створення та оновлення токена, поки не розумію чи це потрібно


class RequestPasswordResetSchema(BaseModel):
    email: EmailStr
    username: str
