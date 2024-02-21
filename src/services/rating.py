from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.repositories.rating import RatingRepo


class RatingService:
    def __init__(self, db: AsyncSession):
        self.repo = RatingRepo(db=db)

    async def set_rate(self, photo_id: int, rate: int,  user_id: UUID):
        result = await self.repo.get_single_rate(photo_id, user_id)
        if result is not None:
            # if we return None - rate was already set
            return None
        else:
            result = await self.repo.set_single_rate(photo_id, rate, user_id)
            return result

    async def delete_rate(self, photo_id: int, rate: int,  user_id: UUID):
        # TODO only for admins or moderators
        result = await self.repo.delete_single_rate(photo_id, user_id)
        return result

    async def get_avg_rate(self, photo_id: int) -> float | None:
        result = await self.repo.get_avg_rate(photo_id)
        if result:
            return round(result, 2)
        return result


