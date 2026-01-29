from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CheckInRequest(BaseModel):
    """Check-in request schema"""
    ticket_code: str = Field(..., min_length=1, max_length=100, description="Unique ticket code")


class CheckInResponse(BaseModel):
    """Check-in response schema"""
    success: bool = Field(..., description="Whether check-in was successful")
    message: str = Field(..., description="Success or error message")
    ticket_id: str = Field(..., description="Ticket ID")
    attendee_name: str = Field(..., description="Attendee name")
    attendee_email: str = Field(..., description="Attendee email")
    event_title: str = Field(..., description="Event title")
    checked_in_at: datetime = Field(..., description="Check-in timestamp")


class ValidateTicketResponse(BaseModel):
    """Validate ticket response schema"""
    valid: bool = Field(..., description="Whether ticket is valid")
    ticket_id: Optional[str] = Field(None, description="Ticket ID if valid")
    attendee_name: Optional[str] = Field(None, description="Attendee name")
    attendee_email: Optional[str] = Field(None, description="Attendee email")
    event_title: Optional[str] = Field(None, description="Event title")
    event_date: Optional[datetime] = Field(None, description="Event date")
    already_checked_in: bool = Field(default=False, description="Whether ticket was already checked in")
    checked_in_at: Optional[datetime] = Field(None, description="Check-in timestamp if already checked in")
    message: str = Field(..., description="Validation message")


class CheckInListItem(BaseModel):
    """Individual check-in item"""
    ticket_id: str
    ticket_code: str
    attendee_name: Optional[str]
    attendee_email: str
    checked_in_at: datetime


class CheckInListResponse(BaseModel):
    """List of check-ins for an event"""
    checkins: list[CheckInListItem]
    total: int
    event_id: str


class ScannerStats(BaseModel):
    """Scanner statistics for an event"""
    event_id: str
    event_title: str
    total_tickets: int
    checked_in: int
    pending: int
    check_in_percentage: float