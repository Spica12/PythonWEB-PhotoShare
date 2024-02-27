from typing import List, Optional

# schemas
from src.schemas.photos import ImageResponseTagsSchema
from src.schemas.comment import CommentResponseIntegratedSchema
from src.schemas.rating import RateExtendedSchema


class ImagePageResponseShortSchema(ImageResponseTagsSchema):
    username: Optional[str] | None
    avg_rating: Optional[float] | None


class ImagePageResponseFullSchema(ImagePageResponseShortSchema):
    comments: Optional[List[CommentResponseIntegratedSchema | None]] = []


class ShowAllRateSchema(RateExtendedSchema):
    username: str
