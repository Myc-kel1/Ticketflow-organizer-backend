# ADD TO: organizer backend → app/api/scanning.py

from fastapi import APIRouter, Depends, status
from typing import Dict, Any

from app.schemas.scan import (
    ScanTicketRequest, ScanTicketResponse,
    AttendeeListResponse, OrderListResponse,
    EventStatsResponse, TicketListResponse, TicketDetailResponse
)
from app.services.scan_service import ScanService
from app.dependencies.permissions import require_organizer

router = APIRouter(tags=["Scanning & Tickets"])


# ── Scan ─────────────────────────────────────────────────────────────────────

@router.post(
    "/events/{event_id}/scan",
    response_model=ScanTicketResponse,
    summary="Scan and validate a ticket QR code"
)
async def scan_ticket(
    event_id: str,
    body: ScanTicketRequest,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    result = ScanService.scan_ticket(
        event_id=event_id,
        ticket_id=body.ticket_id,
        organizer_id=current_user["user_id"]
    )
    return ScanTicketResponse(**result)


# ── Event Stats ───────────────────────────────────────────────────────────────

@router.get(
    "/events/{event_id}/stats",
    response_model=EventStatsResponse,
    summary="Get ticket sales and check-in stats for an event"
)
async def get_event_stats(
    event_id: str,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    result = ScanService.get_event_stats(
        event_id=event_id,
        organizer_id=current_user["user_id"]
    )
    return EventStatsResponse(**result)


# ── Attendees ─────────────────────────────────────────────────────────────────

@router.get(
    "/events/{event_id}/attendees",
    response_model=AttendeeListResponse,
    summary="Get all attendees for an event"
)
async def get_event_attendees(
    event_id: str,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    result = ScanService.get_event_attendees(
        event_id=event_id,
        organizer_id=current_user["user_id"]
    )
    return AttendeeListResponse(**result)


# ── Orders ────────────────────────────────────────────────────────────────────

@router.get(
    "/events/{event_id}/orders",
    response_model=OrderListResponse,
    summary="Get all orders for an event"
)
async def get_event_orders(
    event_id: str,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    result = ScanService.get_event_orders(
        event_id=event_id,
        organizer_id=current_user["user_id"]
    )
    return OrderListResponse(**result)


# ── All Tickets ───────────────────────────────────────────────────────────────

@router.get(
    "/tickets",
    response_model=TicketListResponse,
    summary="Get all tickets across all organizer events"
)
async def get_all_tickets(
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    result = ScanService.get_all_tickets(
        organizer_id=current_user["user_id"]
    )
    return TicketListResponse(**result)


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketDetailResponse,
    summary="Get a single ticket by ID"
)
async def get_ticket(
    ticket_id: str,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    result = ScanService.get_ticket_by_id(
        ticket_id=ticket_id,
        organizer_id=current_user["user_id"]
    )
    return TicketDetailResponse(**result)
