import json
from uuid import UUID

import cloudinary
import cloudinary.api
import cloudinary.uploader
from fastapi import UploadFile

from src.conf.config import config
from src.models.users import UserModel
from sqlalchemy.ext.asyncio import AsyncSession


class CloudinaryService:

    def __init__(self):
        cloudinary.config(
            cloud_name=config.CLOUDINARY_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
            # Use HTTPS with TLS encryption
            secure=True,
        )

    def upload_photo(self, file: UploadFile, user: UserModel):
        folder = f"photoshare/{user.id}"
        result = cloudinary.uploader.upload(file.file, folder=folder, overwrite=True)
        public_id = result["public_id"]

        result_url = cloudinary.CloudinaryImage(public_id).build_url(
            version=result.get("version")
        )

        return result_url, public_id

    def upload_avatar(self, file: UploadFile, user_id: UUID):
        folder = f"photoshare/{user_id}"
        transformation = {
            "gravity": "face",
            "height": 200,
            "width": 200,
            "crop": "crop",
            "radius": "max"
        }
        result = cloudinary.uploader.upload(
            file.file,
            public_id="avatar",
            use_filename=True,
            unique_filename=False,
            folder=folder,
            overwrite=True,
        )
        public_id = result["public_id"]
        avatar_url = cloudinary.CloudinaryImage(public_id).build_url(
            transformation=transformation,
            version=result.get("version")
        )

        return avatar_url

    def destroy_photo(self, public_id: str):
        result = cloudinary.uploader.destroy(public_id, invalidate=True)

        return result

    def get_transformed_photo_url(
        self, public_id: str, request_for_transformation: dict
    ):
        transformation = []
        height = request_for_transformation["height"]
        width = request_for_transformation["width"]
        radius = request_for_transformation["radius"]
        angle = request_for_transformation["angle"]

        if request_for_transformation["zoom_on_face"]:
            transformation.append(self.zoom_on_face())
        if request_for_transformation["rotate_photo"]:
            transformation.append(self.rotate_photo(angle))
        if request_for_transformation["crop_photo"]:
            transformation.append(self.crop_photo(height, width))
        if request_for_transformation["apply_max_radius"]:
            transformation.append(self.apply_max_radius())
        if request_for_transformation["apply_radius"]:
            transformation.append(self.apply_radius(radius))
        if request_for_transformation["apply_grayscale"]:
            transformation.append(self.apply_grayscale())

        transformed_url = cloudinary.CloudinaryImage(public_id).build_url(
            transformation=transformation
        )
        return transformed_url

    def zoom_on_face(self):
        return {"gravity": "face"}

    def rotate_photo(self, angle: int):
        return {"angle": angle}

    def crop_photo(self, height: int, width: int):
        return {"height": height, "width": width, "crop": "crop"}

    def apply_radius(self, radius: int):
        return {"radius": radius}

    def apply_max_radius(self):
        return {"radius": "max"}

    def apply_grayscale(self):
        return {"effect": "grayscale"}
