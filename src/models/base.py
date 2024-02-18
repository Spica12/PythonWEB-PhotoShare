from sqlalchemy.orm import DeclarativeBase

from users import UserModel, TokenModel


class Base(DeclarativeBase):
    pass
