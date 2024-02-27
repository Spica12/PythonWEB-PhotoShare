from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CommentSchema(BaseModel):
    content: str = Field(min_length=3, max_length=255)


class CommentResponseShort(CommentSchema):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentResponseIntegratedSchema(CommentSchema):
    id: int | None
    username: str | None
    updated_at: datetime | None
