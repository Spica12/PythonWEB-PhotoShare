from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import (PhotoModel, RatingModel, TagModel,
                               TransformedImageLinkModel, photos_tags)
from src.models.users import UserModel


class PhotoRepo:

    def __init__(self, db):
        self.db: AsyncSession = db

    async def add_photo(self, user: UserModel, public_id: str, photo_url: str, description: str) -> PhotoModel:
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

    async def get_all_photos(self, skip: int, limit: int):
        stmt = select(PhotoModel).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        # check here. Pycharm:  Expected type 'list[PhotoModel]', got 'Sequence[PhotoModel]' instead
        return result.unique().scalars().all()

    async def get_photo_from_db(self, photo_id: int):
        # to check if the object exists or get one photo by id
        stmt = select(PhotoModel).filter_by(id=photo_id)
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_photo_owner(self, photo_id: int, user_id: UUID):
        # to check if the user is owner of the photo. If result not None = exists
        stmt = select(PhotoModel).filter(
            and_(PhotoModel.id == photo_id, PhotoModel.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def delete_photo(self, photo: PhotoModel):
        await self.db.delete(photo)
        await self.db.commit()

    async def update_photo(self, photo: PhotoModel):
        await self.db.commit()
        await self.db.refresh(photo)
        return photo

    async def add_transformed_photo_to_db(self, photo_id: int, image_url: str):
        new_transformed_photo = TransformedImageLinkModel(
            photo_id=photo_id,
            image_url=image_url
        )
        self.db.add(new_transformed_photo)
        await self.db.commit()
        await self.db.refresh(new_transformed_photo)
        return new_transformed_photo

    async def get_transformed_photo_by_photo_id(self, photo_id: int):
        stmt = select(TransformedImageLinkModel).filter_by(photo_id=photo_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_transformed_photo(self, photo_id: int, transform_id: int):
        stmt = select(TransformedImageLinkModel).filter(
            and_(TransformedImageLinkModel.photo_id == photo_id, TransformedImageLinkModel.id == transform_id)
        )
        result = await self.db.execute(stmt)
        result = result.scalar_one_or_none()
        if result:
            await self.db.delete(result)
            await self.db.commit()

    async def get_transformed_photo_by_transformed_id(self, photo_id: int, transform_id: int):
        stmt = select(TransformedImageLinkModel).filter_by(
            photo_id=photo_id, id=transform_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_photo_object_with_params(self, skip: int, limit: int):
        stmt = (select(PhotoModel.id,
                       PhotoModel.image_url,
                       PhotoModel.description,
                       UserModel.username,
                       func.json_agg(func.distinct(TagModel.name)).label('tags'),
                       func.round(func.avg(RatingModel.value), 2).label('avg_rating')
                       )
                .select_from(UserModel)
                .join(PhotoModel, isouter=True)
                .join(RatingModel, isouter=True)
                .join(photos_tags, isouter=True)
                .join(TagModel, isouter=True)
                .filter(PhotoModel.id.isnot(None))
                .group_by(PhotoModel.id,
                          UserModel.username,
                          PhotoModel.image_url,
                          PhotoModel.description,
                          )
                .offset(skip)
                .limit(limit))
        result = await self.db.execute(stmt)
        return result

    async def get_photo_page(self, photo_id: int, skip: int | None = None, limit: int | None = None):
        stmt = (select(PhotoModel.id,
                       PhotoModel.image_url,
                       PhotoModel.description,
                       UserModel.username,
                       func.json_agg(func.distinct(TagModel.name)).label('tags'),
                       func.round(func.avg(RatingModel.value), 2).label('avg_rating')
                       )
                .select_from(UserModel)
                .join(PhotoModel, isouter=True)
                .join(RatingModel, isouter=True)
                .join(photos_tags, isouter=True)
                .join(TagModel, isouter=True)
                .filter(PhotoModel.id == photo_id)
                .group_by(PhotoModel.id,
                          UserModel.username,
                          PhotoModel.image_url,
                          PhotoModel.description,
                          ))
        result = await self.db.execute(stmt)
        return result.first()

    async def get_picture_count(self, user_id: UUID):
        stmt = select(func.count(PhotoModel.id)).where(PhotoModel.user_id == user_id)
        result = await self.db.execute(stmt)
        result = result.scalar()
        return result
