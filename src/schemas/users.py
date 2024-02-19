from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from src.models.users import Roles


class UserSchema(BaseModel):
    """Pydantic model for validating incoming user registration data."""
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=4, max_length=20)


class UserResponse(BaseModel):
    """Pydantic model for serializing user data in responses."""
    id: int = 1
    username: str
    email: EmailStr
    avatar: str | None
    role: Roles
    picture_count: Optional[int]
    confirmed: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(UserSchema):
    """Pydantic model for validating incoming user update data."""
    # Validation of user input during profile update
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    confirm_password: Optional[str] = None
    avatar: Optional[str] = None


class AnotherUsers(BaseModel):
    """Pydantic model for serializing simplified user data in responses."""
    username: str
    email: EmailStr
    avatar: HttpUrl | None
    role: Roles
    picture_count: Optional[int]
    created_at: datetime


class TokenSchema(BaseModel):
    """
    Pydantic model for serializing JWT tokens.
    """

    # не включаю id, якщо його буде автоматично генерувати база даних.
    # id: int
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    # created_at: datetime
    # updated_at: datetime

    # Поки не включаю час створення та оновлення токена, поки не розумію чи це потрібно
