from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import PhotoModel, TagModel, PhotoTagModel


class TagsRepo:

    def __init__(self, db):
        self.db: AsyncSession = db

    async def create_tag(self, name: str):
        new_tag = TagModel(name=name)
        self.db.add(new_tag)
        await self.db.commit()
        await self.db.refresh(new_tag)
        return new_tag

    async def get_tag_from_db(self, tag: str):
        stmt = select(TagModel).filter_by(name=tag)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def add_tags_to_photo(self, photo_id: int, tags: list[str]) -> None:
        for tag_str in tags:
            # Check if tag exists in db
            tag_str = tag_str.lower().strip()
            stmt = select(TagModel).filter_by(name=tag_str)
            result = await self.db.execute(stmt)
            tag = result.scalar_one_or_none()
            # If not, create new tag
            if not tag:
                tag = TagModel(name=tag_str)
                self.db.add(tag)
                await self.db.commit()
                await self.db.refresh(tag)
            # Check if tag is alredy added to photo
            stmt = select(PhotoTagModel).filter(
                and_(PhotoTagModel.photo_id == photo_id, PhotoTagModel.tag_id == tag.id)
            )
            result = await self.db.execute(stmt)
            exist_photo_tag = result.scalar_one_or_none()
            # If not, add tag to photo
            if not exist_photo_tag:
                photo_tag = PhotoTagModel(photo_id=photo_id, tag_id=tag.id)
                self.db.add(photo_tag)
                await self.db.commit()
