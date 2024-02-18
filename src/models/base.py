from sqlalchemy.orm import DeclarativeBase

from users import UserModel, TokenModel
from photos import PhotoModel, TagModel


class Base(DeclarativeBase):
    pass
