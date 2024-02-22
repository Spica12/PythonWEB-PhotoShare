from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.repositories.rating import RatingRepo
from src.repositories.photos import PhotoRepo
from src.repositories.users import UserRepo


class RatingService:
    def __init__(self, db: AsyncSession):
        self.repo = RatingRepo(db=db)

    async def set_rate(self, photo_id: int, rate: int,  user_id: UUID):
        # TODO rewrite functionality to make one select with join tables.
        photo_owner = await PhotoRepo(self.repo.db).get_photo_owner(photo_id=photo_id, user_id=user_id)
        if photo_owner is not None:
            # if return None - user is the owner of the photo, can't rate own
            return None

        already_set = await self.repo.get_single_rate(photo_id, user_id)

        if already_set is not None:
            # if we return None - rate was already set
            return None
        else:
            result = await self.repo.set_single_rate(photo_id, rate, user_id)
            return result

    async def delete_rate(self, photo_id: int, username:  str):
        # get user UUid by username to work with db
        user = await UserRepo(self.repo.db).get_user_by_username(username=username)
        if user is None:
            return None
        user_id = user.id
        result = await self.repo.delete_single_rate(photo_id, user_id)
        return result

    async def get_avg_rate(self, photo_id: int) -> float | None:
        result = await self.repo.get_avg_rate(photo_id)
        if result:
            return round(result, 2)
        return result


