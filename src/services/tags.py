from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import PhotoModel
from src.models.users import UserModel
from src.repositories.tags import TagRepo


class TagService:

    def __init__(self, db: AsyncSession):
        self.repo = TagRepo(db=db)

    async def add_tags_to_photo(self, photo_id, tags: list[str]) -> None:
        await self.repo.add_tags_to_photo(photo_id, tags)

def normalize_tag(tag: str) -> str:
    # split the string with a comma and replace the spaces with "_"
    normalized_tag = tag.replace(' ', '_').lower().strip()
    return normalized_tag