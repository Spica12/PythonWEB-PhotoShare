from typing import List, Optional

from pydantic import BaseModel, Field

# schemas
from src.schemas.users import UserNameSchema
from src.schemas.photos import ImageUpdateSchema
from src.schemas.rating import RateSchema
from src.schemas.comment import CommentResponseIntegratedSchema


# todo -> ImageSchema
# todo add tags
class ImagePageResponseShortSchema(ImageUpdateSchema):
    # tags: Optional[List[str]] = []
    id: int
    image_url: Optional[str]
    username: Optional[str]#Optional[UserNameSchema]
    value: Optional[int] #Optional[RateSchema]


# todo add tags
class ImagePageResponseFullSchema(ImagePageResponseShortSchema):
    comments: Optional[List[CommentResponseIntegratedSchema]] = []