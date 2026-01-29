from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class EventCreate(BaseModel):
    """Schema for creating a new event"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    location: str = Field(..., min_length=1, max_length=300)
    start_date: str
    end_date: str
    capacity: Optional[int] = Field(None, gt=0)
    ticket_price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)


class EventUpdate(BaseModel):
    """Schema for updating an event (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, min_length=1, max_length=300)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    ticket_price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)


class EventResponse(BaseModel):
    """Schema for event response"""
    id: str
    title: str
    description: Optional[str]
    location: str
    start_date: str
    end_date: str
    capacity: Optional[int]
    ticket_price: Optional[float]
    category: Optional[str]
    organizer_id: str
    image_urls: Optional[list[str]] = []
    created_at: str
    updated_at: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)