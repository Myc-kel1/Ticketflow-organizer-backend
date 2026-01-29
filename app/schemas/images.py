from pydantic import BaseModel, Field
from typing import List


class ImageUploadResponse(BaseModel):
    """Schema for image upload response"""
    event_id: str
    image_urls: List[str] = Field(..., description="Public URLs of uploaded images")
    message: str = "Images uploaded successfully"


class ImageDeleteResponse(BaseModel):
    """Schema for image deletion response"""
    message: str = "Images deleted successfully"
    deleted_count: int