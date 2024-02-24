from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from src.models.photos import PhotoModel
from src.models.users import UserModel
from src.repositories.photos import PhotoRepo
from src.repositories.comments import CommentRepo



class PhotoService:
    def __init__(self, db: AsyncSession):
        self.repo = PhotoRepo(db=db)

    async def get_photo_exists(self, photo_id: int):
        result = await self.repo.get_photo_from_db(photo_id)
        return result

    async def check_photo_owner(self, photo_id: int, user_id: UUID):
        result = await self.repo.get_photo_owner(photo_id, user_id)
        return result

    async def add_photo(self, user: UserModel, public_id: str, photo_url: str, description: str) -> PhotoModel:
        new_photo = await self.repo.add_photo(user, public_id, photo_url, description)

        return new_photo

    async def get_all_photos(self, skip: int, limit: int) -> list[PhotoModel]:
        photos = await self.repo.get_all_photos(skip, limit)
        return photos

    async def delete_photo(self, photo: PhotoModel) -> None:
        await self.repo.delete_photo(photo)

    async def update_photo(self, photo: PhotoModel) -> PhotoModel:
        photo = await self.repo.update_photo(photo)

        return photo

    async def add_transformed_photo_to_db(self, photo_id: int, image_url: str):
        new_transformered_photo = await self.repo.add_transformed_photo_to_db(photo_id, image_url)

        return new_transformered_photo

    async def get_tranformed_photos_by_photo_id(self, photo_id: int):
        tranformed_photos = await self.repo.get_tranformed_photo_by_photo_id(photo_id)
        return tranformed_photos

    async def get_tranformed_photo_by_transformed_id(self, photo_id: int, transform_id: int):
        tranformed_photo = await self.repo.get_tranformed_photo_by_transformed_id(photo_id, transform_id)
        return tranformed_photo

    async def get_all_photo_per_page(self, skip: int, limit: int):
        query = await self.repo.get_photo_object_with_params(skip, limit)
        result = []
        for photo in query:
            logging.info(f"{photo._asdict()}")
            result.append(photo._asdict())
        return result

    async def get_one_photo_page(self, photo_id: int, skip: int, limit: int):
        result = await self.repo.get_photo_page(photo_id, skip, limit)
        if result is not None:
            result = result._asdict()
            comments = await CommentRepo(self.repo.db).get_all_comments(photo_id, skip, limit)
            logging.info(f"{comments}")
            result["comments"] = comments
        logging.info(f"{result}")
        return result
