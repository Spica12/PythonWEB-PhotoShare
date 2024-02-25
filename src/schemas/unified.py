from typing import List, Optional

# schemas
from src.schemas import photos
from src.schemas.comment import CommentResponseIntegratedSchema


class ImagePageResponseShortSchema(photos.ImageResponseTagsSchema):
    username: Optional[str] | None
    avg_rating: Optional[float] | None


class ImagePageResponseFullSchema(ImagePageResponseShortSchema):
    comments: Optional[List[CommentResponseIntegratedSchema | None]] = []
