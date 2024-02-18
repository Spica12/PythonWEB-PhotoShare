from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

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
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Pydantic model for validating incoming user update data."""
    username: str
    email: EmailStr
    password: str


class AnotherUsers(BaseModel):
    """Pydantic model for serializing simplified user data in responses."""
    username: str
    email: EmailStr
    avatar: str
    picture_count: Optional[int]
    created_at: datetime


class TokenSchema(BaseModel):
    """Pydantic model for serializing JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
