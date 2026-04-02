# ADD TO: organizer backend → app/schemas/scan.py

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ScanTicketRequest(BaseModel):
    ticket_id: str


class ScanTicketResponse(BaseModel):
    valid: bool
    ticket_id: str
    message: str
    attendee_name: Optional[str] = None
    attendee_email: Optional[str] = None
    ticket_type: Optional[str] = None
    event_title: Optional[str] = None
    checked_in_at: Optional[str] = None


class AttendeeResponse(BaseModel):
    ticket_id: str
    attendee_name: Optional[str] = None
    attendee_email: Optional[str] = None
    ticket_type: Optional[str] = None
    status: str
    checked_in_at: Optional[str] = None
    purchased_at: str


class AttendeeListResponse(BaseModel):
    attendees: List[AttendeeResponse]
    total: int
    checked_in: int
    pending: int


class OrderItemResponse(BaseModel):
    id: str
    reference: str
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    quantity: int
    amount: float
    status: str
    ticket_type: Optional[str] = None
    created_at: str
    tickets: Optional[List[Dict[str, Any]]] = []


class OrderListResponse(BaseModel):
    orders: List[OrderItemResponse]
    total: int
    total_revenue: float


class EventStatsResponse(BaseModel):
    event_id: str
    event_title: str
    total_capacity: Optional[int] = None
    tickets_sold: int
    tickets_checked_in: int
    tickets_active: int
    total_revenue: float
    check_in_rate: float
    sold_out: bool
    ticket_type_breakdown: List[Dict[str, Any]]


class TicketDetailResponse(BaseModel):
    id: str
    event_id: str
    event_title: Optional[str] = None
    order_id: Optional[str] = None
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    ticket_type: Optional[str] = None
    status: str
    qr_code_url: Optional[str] = None
    checked_in_at: Optional[str] = None
    created_at: str


class TicketListResponse(BaseModel):
    tickets: List[TicketDetailResponse]
    total: int
