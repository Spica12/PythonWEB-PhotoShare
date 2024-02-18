from sqlalchemy.orm import DeclarativeBase

from users import UserModel, TokenModel
from photos import (
    PhotoModel,
    TransformedImageLinkModel,
    TagModel,
    PhotoTagModel,
    CommentModel,
    RatingModel,
)


class Base(DeclarativeBase):
    pass
