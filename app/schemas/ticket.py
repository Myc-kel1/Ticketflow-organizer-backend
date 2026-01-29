from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class TicketStatus(str, Enum):
    """Ticket status enum"""
    ACTIVE = "active"
    CHECKED_IN = "checked_in"
    CANCELLED = "cancelled"


class TicketCreate(BaseModel):
    """Schema for creating a ticket"""
    event_id: str = Field(..., description="Event ID")
    attendee_email: EmailStr = Field(..., description="Attendee email")
    attendee_name: Optional[str] = Field(None, max_length=255, description="Attendee name")
    price: float = Field(..., ge=0, description="Ticket price")


class TicketResponse(BaseModel):
    """Ticket response schema"""
    id: str
    event_id: str
    attendee_id: str
    attendee_email: str
    attendee_name: Optional[str] = None
    ticket_code: str
    status: TicketStatus
    price: float
    purchased_at: datetime
    checked_in_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TicketStats(BaseModel):
    """Ticket statistics schema"""
    event_id: str
    total_sold: int = Field(..., description="Total tickets sold (excluding cancelled)")
    checked_in: int = Field(..., description="Number of checked-in tickets")
    pending: int = Field(..., description="Number of active/pending tickets")
    cancelled: int = Field(..., description="Number of cancelled tickets")


class TicketListResponse(BaseModel):
    """List of tickets with metadata"""
    tickets: list[TicketResponse]
    total: int
    event_id: str


class CancelTicketResponse(BaseModel):
    """Response for ticket cancellation"""
    message: str = "Ticket cancelled successfully"
    ticket_id: str
    cancelled_at: datetime