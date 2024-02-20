import json

import cloudinary
import cloudinary.api
import cloudinary.uploader
from fastapi import UploadFile

from src.conf.config import config
from src.models.users import UserModel


class CloudinaryService:

    def __init__(self):
        cloudinary.config(
            cloud_name=config.CLOUDINARY_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
            # Use HTTPS with TLS encryption
            secure=True
        )

    def upload_photo(self, file: UploadFile, user: UserModel):
        folder = f"photoshare/{user.username}"
        result = cloudinary.uploader.upload(
            file.file, folder=folder, overwrite=True
        )
        public_id = result["public_id"]
        result_url = cloudinary.CloudinaryImage(public_id).build_url(version=result.get("version"))

        return result_url

#     def get_asset_info(self, public_id):
#         image_info = cloudinary.api.resource(public_id)
#         print("****3. Get and use details of the image****\nUpload response:\n", json.dumps(image_info, indent=2), "\n")

#         # Assign tags based on image width
#         width = image_info.get("width", 0)
#         if width > 900:
#             self.update_tags(public_id, tags="large")
#         elif width > 500:
#             self.update_tags(public_id, tags="medium")
#         else:
#             self.update_tags(public_id, tags="small")

#     def update_tags(self, public_id, tags):
#         update_resp = cloudinary.api.update(public_id, tags=tags)
#         print("New tag: ", update_resp["tags"], "\n")

#     def create_photo_tag(self, public_id, transformations):
#         # Transform the image and create an image tag
#         image_tag = cloudinary.CloudinaryImage(public_id).image(**transformations)

#         # Log the image tag to the console
#         print("****4. Transform the image****\nImage Tag: ", image_tag, "\n")

# def main():
#     cloudinary_service = CloudinaryService("cloud_name", "api_key", "api_secret")

#     # Upload an image
#     cloudinary_service.upload_photo("https://cloudinary-devs.github.io/cld-docs-assets/assets/images/butterfly.jpeg",
#                                     public_id="quickstart_butterfly", unique_filename=False, overwrite=True)

#     # Get and use details of the image
#     cloudinary_service.get_asset_info("quickstart_butterfly")

#     # Create photo tag with transformations
#     transformations = {
#         'radius': 'max',
#         'effect': 'sepia'
#     }
#     cloudinary_service.create_photo_tag("quickstart_butterfly", transformations)
