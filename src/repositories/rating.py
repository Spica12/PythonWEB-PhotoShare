from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import RatingModel
from src.models.users import UserModel


class RatingRepo:
    def __init__(self, db):
        self.db: AsyncSession = db

    async def set_single_rate(self, photo_id: int, rate: int, user_id: UUID):
        new_rate = RatingModel(value=rate, photo_id=photo_id, user_id=user_id)
        self.db.add(new_rate)
        await self.db.commit()
        await self.db.refresh(new_rate)
        return new_rate

    async def get_single_rate(self, photo_id: int, user_id: UUID):
        # to check if user already set a rate
        """
        The get_single_rate function is used to check if a user has already rated a photo.
        It takes in the photo_id and user_id as parameters, and returns the result of an SQL query that checks if there is any row in the RatingModel table where both conditions are met.


        :param self: Represent the instance of the object itself
        :param photo_id: int: Get the photo id from the database
        :param user_id: UUID: Check if the user already set a rate
        :return: A single rate for a photo or none if no such rate exists
        :doc-author: Trelent
        """
        stmt = select(RatingModel).filter(
            and_(RatingModel.photo_id == photo_id, RatingModel.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_rates(self, photo_id: int):
        """
        The get_rates function returns a list of all the ratings for a given photo.
        The function takes in one parameter, which is the id of the photo to be rated.
        It then uses that id to query our database and return all ratings associated with that photo.

        :param self: Represent the instance of a class
        :param photo_id: int: Filter the query to only return ratings for a specific photo
        :return: A list of dictionaries, each dictionary representing a rating
        :doc-author: Trelent
        """
        stmt = (select(RatingModel.id,
                       RatingModel.value,
                       RatingModel.photo_id,
                       RatingModel.created_at,
                       UserModel.username.label('username')
                       )
                .join(UserModel)
                .filter(RatingModel.photo_id == photo_id))
        result = await self.db.execute(stmt)
        result = result.all()
        return result

    async def delete_single_rate(self, photo_id: int, user_id: UUID):
        # only for admins
        stmt = select(RatingModel).filter(
            and_(RatingModel.photo_id == photo_id, RatingModel.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        result = result.scalar_one_or_none()
        if result:
            await self.db.delete(result)
            await self.db.commit()
        return result
