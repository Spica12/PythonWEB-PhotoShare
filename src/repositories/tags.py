from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import PhotoModel, TagModel


class TagRepo:

    def __init__(self, db):
        self.db: AsyncSession = db

    async def add_tags_to_photo(self, photo_id: int, tags_list: list[str]) -> None:
        tags = []
        for tag_str in tags_list:
            tag_name = tag_str.lower().strip()
            stmt = select(TagModel).filter_by(name=tag_name)
            result = await self.db.execute(stmt)
            tag = result.scalar_one_or_none()
            if tag is None:
                tag = TagModel(name=tag_name)
                self.db.add(tag)
                await self.db.commit()
                await self.db.refresh(tag)
            tags.append(tag)

        photo = await self.db.get(PhotoModel, photo_id)
        photo.tags = tags
        await self.db.commit()
