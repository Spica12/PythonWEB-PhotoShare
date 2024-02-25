from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CommentSchema(BaseModel):
    """Pydantic model for validating incoming comment data."""
    content: str = Field(min_length=3, max_length=255)


class CommentResponseShort(CommentSchema):
    """Pydantic model for serializing comment data in responses."""
    id: int
    user_id: UUID
    photo_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentResponseIntegratedSchema(CommentSchema):
    # todo change uid by username
    user_id: UUID
    created_at: datetime
