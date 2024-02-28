from io import BytesIO
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from PIL import Image

from src.conf.config import config
from src.conf import messages
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
        new_transformed_photo = await self.repo.add_transformed_photo_to_db(photo_id, image_url)
        return new_transformed_photo

    async def get_transformed_photos_by_photo_id(self, photo_id: int):
        transformed_photos = await self.repo.get_transformed_photo_by_photo_id(photo_id)
        return transformed_photos

    async def get_transformed_photo_by_transformed_id(self, photo_id: int, transform_id: int):
        transformed_photo = await self.repo.get_transformed_photo_by_transformed_id(photo_id, transform_id)
        return transformed_photo

    async def delete_transformed_photo(self, photo_id: int, transform_id: int):
        await self.repo.delete_transformed_photo(photo_id, transform_id)

    async def get_all_photo_per_page(self, skip: int, limit: int):
        query = await self.repo.get_photo_object_with_params(skip, limit)
        result = []
        for photo in query:
            result.append(photo._asdict())
        return result

    async def get_one_photo_page(self, photo_id: int, skip: int, limit: int):
        result = await self.repo.get_photo_page(photo_id, skip, limit)
        if result is not None:
            # if we find photo
            # translate result to dict
            result = result._asdict()
            comments = await CommentRepo(self.repo.db).get_all_comments(photo_id, skip, limit)
            # adding comments to result dict
            result["comments"] = comments
        return result

    async def validate_photo(self, file: UploadFile):
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.INVALID_FILE_NOT_IMAGE,
        )
        contents = await file.read()
        if len(contents) > config.MAX_FILE_SIZE_BYTES:
            print(len(contents))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.TOO_BIG_FILE,
            )
        await file.seek(0)
        try:
            img = Image.open(BytesIO(contents))
            img.verify()
        except Exception as e:
            raise HTTPException(status_code=400, detail=messages.INVALID_FILE_NOT_IMAGE)
