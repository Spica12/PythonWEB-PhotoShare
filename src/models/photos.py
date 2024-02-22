from datetime import datetime

from src.models.base import Base
from src.models.users import UserModel
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PhotoModel(Base):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String(255), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    user: Mapped[UserModel] = relationship("UserModel", backref="photos")
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )


class TransformedImageLinkModel(Base):
    __tablename__ = "transformed_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id"), nullable=False)
    photo: Mapped[PhotoModel] = relationship("PhotoModel", backref="transformed_images")
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )


class TagModel(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)


class PhotoTagModel(Base):
    __tablename__ = "photos_tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id"), nullable=False)
    photo: Mapped[PhotoModel] = relationship("PhotoModel", backref="tags")
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), nullable=False)
    tag: Mapped[TagModel] = relationship("TagModel", backref="photos")
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )


class CommentModel(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id"), nullable=False)
    photo: Mapped[PhotoModel] = relationship("PhotoModel", backref="comments")
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    user: Mapped[UserModel] = relationship("UserModel", backref="comments")
    # editor_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )


class RatingModel(Base):
    __tablename__ = "ratings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id"), nullable=False)
    photo: Mapped[PhotoModel] = relationship("PhotoModel", backref="ratings")
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    user: Mapped[UserModel] = relationship("UserModel", backref="ratings")
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
