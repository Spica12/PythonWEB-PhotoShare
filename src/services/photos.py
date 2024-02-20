from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import PhotoModel
from src.models.users import UserModel
from src.repositories.photos import PhotoRepo


class PhotoService:

    def __init__(self, db: AsyncSession):
        """
        The __init__ function is called when the class is instantiated.
        It's used to initialize variables and do other setup tasks that need to be done every time an object of this class is created.

        :param self: Represent the instance of the class
        :param db: AsyncSession: Create a connection to the database
        :return: Nothing
        """
        self.repo = PhotoRepo(db=db)

    async def add_photo(self, user: UserModel, photo_url: str, description: str) -> PhotoModel:
        new_photo = await self.repo.add_photo(user, photo_url, description)

        return new_photo

    async def get_all_photos(self, user: UserModel, skip: int, limit: int) -> list[PhotoModel]:
        photos = await self.repo.get_all_photos(user, skip, limit)

        return photos
