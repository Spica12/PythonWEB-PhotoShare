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

class TransformRequestSchema(BaseModel):
    width: Optional[int] = Field(None, description="Width of the image")
    height: Optional[int] = Field(None, description="Height of the image")
    crop: Optional[str] = Field(None, description="Crop mode for the image (e.g., 'fill', 'fit', 'scale')")
    gravity: Optional[str] = Field(None, description="Gravity mode for the image (e.g., 'center', 'north', 'south')")
    format: Optional[str] = Field(None, description="Format of the image")
    quality: Optional[int] = Field(None, description="Quality of the image (1-100)")
    radius: Optional[int] = Field(None, description="Radius for rounded corners")
    effect: Optional[str] = Field(None, description="Effect to apply to the image")
    angle: Optional[int] = Field(None, description="Angle of rotation")
    overlay: Optional[str] = Field(None, description="Public ID of an overlay image")
    opacity: Optional[int] = Field(None, description="Opacity of the overlay image (0-100)")
    border: Optional[str] = Field(None, description="Border settings for the image")
    background: Optional[str] = Field(None, description="Background color for the image")
