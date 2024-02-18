from sqlalchemy.orm import DeclarativeBase

from users import UserModel, TokenModel
from photos import PhotoModel, TransformedImageLinkModel, TagModel, PhotoTagModel, CommentModel


class Base(DeclarativeBase):
    pass
