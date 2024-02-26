from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import PhotoModel
from src.models.users import UserModel
from src.repositories.tags import TagRepo


class TagService:

    def __init__(self, db: AsyncSession):
        self.repo = TagRepo(db=db)

    async def add_tags_to_photo(self, photo_id, tags: list[str]) -> None:
        await self.repo.add_tags_to_photo(photo_id, tags)

    def normalize_list_of_tag(body_tags: str) -> str:
        # split the string with a comma and replace the spaces with "_"
        list_tags = []
        for tag in body_tags.split(","):
            tag = tag.replace(' ', '_').lower().strip()
            list_tags.append(tag)

        return list_tags
