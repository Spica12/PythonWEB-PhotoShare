from datetime import datetime
from typing import Dict, Optional, Union

from pydantic import BaseModel, Field


class TransformSchema(BaseModel):
    transformation_params: Dict[str, Union[str, int]] = Field(
        default_factory=dict,
        example={
            "width": 500,
            "height": 300,
            "crop": "fill",
            "effect": "grayscale",
            "border": "5px_solid_lightblue",
            "angle": 15,
        },
    )


class TransformResponse(BaseModel):
    id: int
    original_picture_id: int
    url: str
    qr_url: Optional[str]
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class TransformRequestSchema(BaseModel):
    width: Optional[int] = Field(default=200, description="Width of the image")
    height: Optional[int] = Field(default=200, description="Height of the image")
    # crop: Optional[str] = Field(None, description="Crop mode for the image (e.g., 'fill', 'fit', 'scale')")
    # gravity: Optional[str] = Field(None, description="Gravity mode for the image (e.g., 'center', 'north', 'south')")
    # format: Optional[str] = Field(None, description="Format of the image")
    # quality: Optional[int] = Field(None, description="Quality of the image (1-100)")
    radius: Optional[int] = Field(default=50, description="Radius for rounded corners")
    # effect: Optional[str] = Field(None, description="Effect to apply to the image")
    angle: Optional[int] = Field(default=45, description="Angle of rotation")
    # overlay: Optional[str] = Field(None, description="Public ID of an overlay image")
    # opacity: Optional[int] = Field(None, description="Opacity of the overlay image (0-100)")
    # border: Optional[str] = Field(None, description="Border settings for the image")
    # background: Optional[str] = Field(None, description="Background color for the image")
    zoom_on_face: Optional[bool] = Field(default=False, description="Zoom on face")
    rotate_photo: Optional[bool] = Field(default=False, description="Rotate photo")
    crop_photo: Optional[bool] = Field(default=False, description="Crop photo")
    apply_max_radius: Optional[bool] = Field(default=False, description="Max radius")
    apply_radius: Optional[bool] = Field(default=False, description="Apply radius")
    apply_grayscale: Optional[bool] = Field(default=False, description="Apply grayscale")
