from datetime import datetime
from typing import Optional, Dict, Union

from pydantic import BaseModel, Field


class TransformSchema(BaseModel):
    """Pydantic model for validating incoming transformation parameters."""
    transformation_params: Dict[str, Union[str, int]] = Field(
        default_factory=dict,
        example={"width": 500, "height": 300,
                 "crop": "fill",
                 "effect": "grayscale",
                 "border": "5px_solid_lightblue",
                 "angle": 15,
                 }
    )


class TransformResponse(BaseModel):
    """Pydantic model for serializing transformation data in responses."""
    id: int
    original_picture_id: int
    url: str
    qr_url: Optional[str]
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True