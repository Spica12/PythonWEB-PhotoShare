from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.photos import PhotoRepo


class PhotoService:
    # def __init__(self, db: AsyncSession):
    #     self.repo = PhotoRepo(db=db)

    async def get_photo_exists(self, photo_id: int, db: AsyncSession):
        result = await PhotoRepo(db).get_photo_from_db(photo_id)
        return result


photo_service = PhotoService()
