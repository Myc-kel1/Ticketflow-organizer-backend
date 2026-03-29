# ADD THIS FILE TO: your organizer backend → app/api/ticket_types.py

from fastapi import APIRouter, Depends, status
from typing import List, Dict, Any

from app.schemas.ticket_type import TicketTypeCreate, TicketTypeUpdate, TicketTypeResponse
from app.services.ticket_type_service import TicketTypeService
from app.dependencies.permissions import require_organizer

router = APIRouter(
    prefix="/events/{event_id}/ticket-types",
    tags=["Ticket Types"]
)


@router.post(
    "",
    response_model=TicketTypeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ticket type for an event"
)
async def create_ticket_type(
    event_id: str,
    body: TicketTypeCreate,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    result = TicketTypeService.create_ticket_type(
        event_id=event_id,
        organizer_id=current_user["user_id"],
        name=body.name,
        price=body.price,
        quantity_available=body.quantity_available,
        description=body.description,
        is_active=body.is_active
    )
    return TicketTypeResponse(**result)


@router.get(
    "",
    response_model=List[TicketTypeResponse],
    summary="List all ticket types for an event"
)
async def get_ticket_types(
    event_id: str,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    results = TicketTypeService.get_ticket_types(
        event_id=event_id,
        organizer_id=current_user["user_id"]
    )
    return [TicketTypeResponse(**r) for r in results]


@router.get(
    "/{ticket_type_id}",
    response_model=TicketTypeResponse,
    summary="Get a single ticket type by ID"
)
async def get_ticket_type(
    event_id: str,
    ticket_type_id: str,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    result = TicketTypeService.get_ticket_type_by_id(
        ticket_type_id=ticket_type_id,
        event_id=event_id,
        organizer_id=current_user["user_id"]
    )
    return TicketTypeResponse(**result)


@router.patch(
    "/{ticket_type_id}",
    response_model=TicketTypeResponse,
    summary="Update a ticket type"
)
async def update_ticket_type(
    event_id: str,
    ticket_type_id: str,
    body: TicketTypeUpdate,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    result = TicketTypeService.update_ticket_type(
        ticket_type_id=ticket_type_id,
        event_id=event_id,
        organizer_id=current_user["user_id"],
        updates=body.model_dump(exclude_none=True)
    )
    return TicketTypeResponse(**result)


@router.delete(
    "/{ticket_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a ticket type (only if no tickets sold)"
)
async def delete_ticket_type(
    event_id: str,
    ticket_type_id: str,
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    TicketTypeService.delete_ticket_type(
        ticket_type_id=ticket_type_id,
        event_id=event_id,
        organizer_id=current_user["user_id"]
    )
