import logging

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

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
        stmt = select(RatingModel).filter(
            and_(RatingModel.photo_id == photo_id, RatingModel.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_rates(self, photo_id: int):
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
