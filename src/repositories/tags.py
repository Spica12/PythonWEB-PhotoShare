from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import TagModel, PhotoTagModel


class TagRepo:

    def __init__(self, db):
        self.db: AsyncSession = db

    async def create_tag(self, name: str):
        new_tag = TagModel(name=name)
        self.db.add(new_tag)
        await self.db.commit()
        await self.db.refresh(new_tag)
        return new_tag

    async def get_tag_by_name(self, tag: str):
        stmt = select(TagModel).filter_by(name=tag)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_tag_to_photo(self, photo_id: int, tag_id: int) -> None:
        photo_tag = PhotoTagModel(photo_id=photo_id, tag_id=tag_id)
        self.db.add(photo_tag)
        await self.db.commit(
    )

    async def get_photo_tag_by_id(self, photo_id: int, tag_id: id):
        stmt = select(PhotoTagModel).filter(
            and_(PhotoTagModel.photo_id == photo_id, PhotoTagModel.tag_id == tag_id)
        )
        result = await self.db.execute(stmt)
        exist_photo_tag = result.scalar_one_or_none()
        return exist_photo_tag

    async def add_tags_to_photo(self, photo_id: int, tags: list[str]) -> None:
        for tag_str in tags:
            tag_name = tag_str.lower().strip()
            # Check if tag exists in db
            tag = await self.get_tag_by_name(tag_name)
            # If not, create new tag
            if not tag:
                tag = await self.create_tag(tag_name)
            # Check if tag is alredy added to photo
            exist_photo_tag = await self.get_photo_tag_by_id(photo_id, tag.id)
            # If not, add tag to photo
            if not exist_photo_tag:
                photo_tag = await self.add_tag_to_photo(photo_id, tag.id)
