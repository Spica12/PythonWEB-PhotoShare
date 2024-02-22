from uuid import UUID

from pydantic import BaseModel, Field


class SetRateSchema(BaseModel):
    value: int = Field(5, ge=1, le=5)


class RateResponseSchema(SetRateSchema):
    photo_id: int
    user_id: UUID

    class Config:
        from_attributes = True
