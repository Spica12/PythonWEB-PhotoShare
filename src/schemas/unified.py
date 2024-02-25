from typing import List, Optional

from pydantic import BaseModel

# schemas
from src.schemas.users import UserNameSchema
from src.schemas import photos
from src.schemas.rating import RateSchema
from src.schemas.comment import CommentResponseIntegratedSchema


class ImagePageResponseShortSchema(photos.ImageResponseTagsSchema):
    username: Optional[str]#Optional[UserNameSchema]
    value: Optional[int] #Optional[RateSchema]


class ImagePageResponseFullSchema(ImagePageResponseShortSchema):
    comments: Optional[List[CommentResponseIntegratedSchema]] = []
