from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import PhotoModel
from src.models.users import UserModel


class PhotoRepo:

    def __init__(self, db):
        self.db: AsyncSession = db

    async def add_photo(
        self, user: UserModel, public_id: str, photo_url: str, description: str
    ) -> PhotoModel:
        new_photo = PhotoModel(
            public_id=public_id,
            image_url=photo_url,
            user_id=user.id,
            description=description
        )
        self.db.add(new_photo)
        await self.db.commit()
        await self.db.refresh(new_photo)

        return new_photo

    async def get_all_photos(
        self, skip: int, limit: int
    ) -> list[PhotoModel]:
        stmt = select(PhotoModel).offset(skip).limit(limit)
        result = await self.db.execute(stmt)

        # check here. Pycharm:  Expected type 'list[PhotoModel]', got 'Sequence[PhotoModel]' instead
        return result.scalars().all()

    # to check if the object exists or get one photo by id
    async def get_photo_from_db(self, photo_id: int):
        stmt = select(PhotoModel).filter_by(id=photo_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
