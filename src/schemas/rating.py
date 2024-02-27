from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RateSchema(BaseModel):
    value: int


class RateExtendedSchema(RateSchema):
    id: int
    photo_id: int
    created_at: datetime


class SetRateSchema(RateSchema):
    value: int = Field(5, ge=1, le=5)


class RateResponseSchema(SetRateSchema):
    photo_id: int
    user_id: UUID

    class Config:
        from_attributes = True
