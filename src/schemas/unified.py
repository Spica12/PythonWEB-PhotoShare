from typing import List, Optional

# schemas
from src.schemas import photos
from src.schemas.comment import CommentResponseIntegratedSchema


class ImagePageResponseShortSchema(photos.ImageResponseTagsSchema):
    username: Optional[str]
    avg_rating: Optional[float]


class ImagePageResponseFullSchema(ImagePageResponseShortSchema):
    comments: Optional[List[CommentResponseIntegratedSchema]] = []
