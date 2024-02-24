import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import File, UploadFile

from pydantic import BaseModel, Field


class ImageSchema(BaseModel):
    """Pydantic model for validating incoming picture data."""
    file: UploadFile = File()
    description: Optional[str] = Field(max_length=255)
    tags: Optional[str] = None
    tags: Optional[str] = None


class ImageUpdateSchema(BaseModel):
    """Pydantic model for validating incoming picture update data."""

    description: Optional[str] = Field(max_length=255)


class ImageResponseAfterCreateSchema(BaseModel):
    """Pydantic model for serializing picture data after creating in responses."""

    # TODO
    # This is test schema. Need to think how to do better
    id: int
    public_id: str
    image_url: str
    user_id: uuid.UUID
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ImageResponseSchema(BaseModel):
    """Pydantic model for serializing picture data in responses."""

    user_id: uuid.UUID
    id: int
    image_url: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    rating: Optional[int] = 0
    created_at: datetime
    updated_at: datetime
    comments: Optional[List[str]] = []
