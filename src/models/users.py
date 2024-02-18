import enum
import uuid
from datetime import datetime

from base import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Roles(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    users: str = "users"


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Roles] = mapped_column(Enum(Roles), default=Roles.users, nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )


class TokenModel(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("users.id"), nullable=False
    )
    user: Mapped[UserModel] = relationship("UserModel", backref="tokens")
    created_at: Mapped[DateTime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
