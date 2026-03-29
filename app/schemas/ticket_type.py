# ADD THIS FILE TO: your organizer backend → app/schemas/ticket_type.py

from pydantic import BaseModel, Field
from typing import Optional, List


class TicketTypeCreate(BaseModel):
    name: str = Field(..., min_length=1, description="e.g. Regular, Premium, VIP")
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    quantity_available: int = Field(..., ge=1)
    is_active: bool = True


class TicketTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    quantity_available: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class TicketTypeResponse(BaseModel):
    id: str
    event_id: str
    name: str
    description: Optional[str] = None
    price: float
    quantity_available: int
    quantity_sold: int
    quantity_remaining: int
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
