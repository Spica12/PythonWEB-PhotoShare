from datetime import datetime

from pydantic import BaseModel, Field


class CommentSchema(BaseModel):
    """Pydantic model for validating incoming comment data."""
    content: str = Field(min_length=3, max_length=255)


class CommentResponse(CommentSchema):
    """Pydantic model for serializing comment data in responses."""
    id: int
    user_id: int
    photo_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
