from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import PhotoModel


class PhotoRepo:

    def __init__(self, db):
        self.db: AsyncSession = db

    # to check if the object exists or get one photo by id
    async def get_photo_from_db(self, photo_id: int):
        stmt = select(PhotoModel).filter_by(id=photo_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
