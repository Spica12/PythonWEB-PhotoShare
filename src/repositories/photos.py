from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import CommentModel, PhotoModel
from src.models.users import UserModel


class PhotoRepo:

    def __init__(self, db):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the database connection and creates a new session for each request.

        :param self: Represent the instance of the class
        :param db: Pass in a database connection to the class
        :return: Nothing
        """
        self.db: AsyncSession = db

    async def add_photo(self, user: UserModel, photo_url: str, description: str) -> PhotoModel:
        new_photo = PhotoModel(
            image_url=photo_url,
            user_id=user.id,
            description=description
        )
        self.db.add(new_photo)
        await self.db.commit()
        await self.db.refresh(new_photo)

        return new_photo

    async def get_all_photos(
        self, user: UserModel, skip: int, limit: int
    ) -> list[PhotoModel]:
        stmt = select(PhotoModel).filter_by(user_id=user.id).offset(skip).limit(limit)
        result = await self.db.execute(stmt)

        return result.scalars().all()
