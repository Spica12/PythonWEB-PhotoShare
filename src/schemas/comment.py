from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CommentSchema(BaseModel):
    content: str = Field(min_length=3, max_length=255)


class CommentResponseShort(CommentSchema):
    # todo change uuuid to username ???
    id: int
    user_id: UUID
    photo_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentResponseIntegratedSchema(CommentSchema):
    # todo change uid by username
    username: str | None
    updated_at: datetime | None
