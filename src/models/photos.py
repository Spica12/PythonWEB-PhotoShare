from datetime import datetime

from src.models.base import Base
from src.models.users import UserModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


photos_tags = Table(
    "photos_tags",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photos.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)


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
    transformed_images: Mapped[list["TransformedImageLinkModel"]] = relationship(
        "TransformedImageLinkModel",
        cascade="all, delete-orphan",
        back_populates="photo",
        lazy="joined",
    )
    comments: Mapped[list["CommentModel"]] = relationship(
        "CommentModel",
        cascade="all, delete-orphan",
        back_populates="photo",
        lazy="joined",
    )
    ratings: Mapped[list["RatingModel"]] = relationship(
        "RatingModel",
        cascade="all, delete-orphan",
        back_populates="photo",
        lazy="joined",
    )
    tags: Mapped[list["TagModel"]] = relationship(
        secondary=photos_tags,
        cascade="save-update, merge",
        back_populates="photos",
        single_parent=True,
        lazy="joined",
    )


class TagModel(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    photos: Mapped[list["PhotoModel"]] = relationship(
        "PhotoModel", secondary=photos_tags, back_populates="tags"
    )


class TransformedImageLinkModel(Base):
    __tablename__ = "transformed_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    photo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    photo: Mapped[PhotoModel] = relationship(
        "PhotoModel", back_populates="transformed_images"
    )
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )


class CommentModel(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    photo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    photo: Mapped[PhotoModel] = relationship("PhotoModel", back_populates="comments")
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    user: Mapped[UserModel] = relationship(
        "UserModel", backref="comments"
    )
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
    photo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    photo: Mapped[PhotoModel] = relationship(
        "PhotoModel", back_populates="ratings"
    )
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    user: Mapped[UserModel] = relationship(
        "UserModel", backref="ratings"
    )
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
