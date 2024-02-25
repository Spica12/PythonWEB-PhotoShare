import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import File, UploadFile

from pydantic import BaseModel, Field


class ImageUpdateSchema(BaseModel):
    description: Optional[str] = Field(max_length=255)


class ImageSchema(ImageUpdateSchema):
    file: UploadFile = File()
    tags: Optional[str] = None


class ImageBaseResponseSchema(BaseModel):
    id: int
    image_url: str
    description: Optional[str] = None


class ImageResponseRatingSchema(ImageBaseResponseSchema):
    rating: Optional[int] = 0


class ImageResponseTagsSchema(ImageBaseResponseSchema):
    tags: Optional[List[str]] = []


class ImageExtendedResponseSchema(ImageResponseRatingSchema):
    tags: Optional[List[str]] = []
    created_at: datetime


class ImageResponseAfterCreateSchema(ImageBaseResponseSchema):
    # TODO
    # This is test schema. Need to think how to do better
    public_id: str
    user_id: uuid.UUID
    created_at: datetime
    # updated_at: datetime


class ImageResponseSchema(ImageExtendedResponseSchema):
    user_id: uuid.UUID
    # tags: Optional[List[str]] = []
    # rating: Optional[int] = 0
    # created_at: datetime
    updated_at: datetime
    comments: Optional[List[str]] = []
