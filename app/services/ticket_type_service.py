# ADD THIS FILE TO: your organizer backend → app/services/ticket_type_service.py

from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from app.core.supabase import supabase


class TicketTypeService:

    @staticmethod
    def _verify_event_ownership(event_id: str, organizer_id: str) -> None:
        """Confirm this event belongs to the organizer making the request."""
        result = supabase.table("events")\
            .select("id")\
            .eq("id", event_id)\
            .eq("organizer_id", organizer_id)\
            .single()\
            .execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found or you do not have permission to manage it"
            )

    @staticmethod
    def _format(ticket_type: Dict[str, Any]) -> Dict[str, Any]:
        """Add computed quantity_remaining field."""
        ticket_type["quantity_remaining"] = (
            ticket_type["quantity_available"] - ticket_type["quantity_sold"]
        )
        return ticket_type

    @staticmethod
    def create_ticket_type(
        event_id: str,
        organizer_id: str,
        name: str,
        price: float,
        quantity_available: int,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> Dict[str, Any]:
        TicketTypeService._verify_event_ownership(event_id, organizer_id)

        # Prevent duplicate names on the same event
        existing = supabase.table("ticket_types")\
            .select("id")\
            .eq("event_id", event_id)\
            .ilike("name", name)\
            .execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A ticket type named '{name}' already exists for this event"
            )

        result = supabase.table("ticket_types").insert({
            "event_id": event_id,
            "name": name,
            "description": description,
            "price": price,
            "quantity_available": quantity_available,
            "quantity_sold": 0,
            "is_active": is_active
        }).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create ticket type"
            )

        return TicketTypeService._format(result.data[0])

    @staticmethod
    def get_ticket_types(event_id: str, organizer_id: str) -> List[Dict[str, Any]]:
        TicketTypeService._verify_event_ownership(event_id, organizer_id)

        result = supabase.table("ticket_types")\
            .select("*")\
            .eq("event_id", event_id)\
            .order("created_at", desc=False)\
            .execute()

        return [TicketTypeService._format(t) for t in (result.data or [])]

    @staticmethod
    def get_ticket_type_by_id(
        ticket_type_id: str,
        event_id: str,
        organizer_id: str
    ) -> Dict[str, Any]:
        TicketTypeService._verify_event_ownership(event_id, organizer_id)

        result = supabase.table("ticket_types")\
            .select("*")\
            .eq("id", ticket_type_id)\
            .eq("event_id", event_id)\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket type not found"
            )

        return TicketTypeService._format(result.data)

    @staticmethod
    def update_ticket_type(
        ticket_type_id: str,
        event_id: str,
        organizer_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        TicketTypeService._verify_event_ownership(event_id, organizer_id)

        # Confirm ticket type exists on this event
        existing = supabase.table("ticket_types")\
            .select("*")\
            .eq("id", ticket_type_id)\
            .eq("event_id", event_id)\
            .single()\
            .execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket type not found"
            )

        # Cannot reduce quantity_available below quantity_sold
        if "quantity_available" in updates:
            sold = existing.data["quantity_sold"]
            if updates["quantity_available"] < sold:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot set quantity below the number already sold ({sold})"
                )

        clean = {k: v for k, v in updates.items() if v is not None}
        if not clean:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )

        result = supabase.table("ticket_types")\
            .update(clean)\
            .eq("id", ticket_type_id)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update ticket type"
            )

        return TicketTypeService._format(result.data[0])

    @staticmethod
    def delete_ticket_type(
        ticket_type_id: str,
        event_id: str,
        organizer_id: str
    ) -> None:
        TicketTypeService._verify_event_ownership(event_id, organizer_id)

        # Cannot delete if tickets have already been sold
        existing = supabase.table("ticket_types")\
            .select("quantity_sold")\
            .eq("id", ticket_type_id)\
            .eq("event_id", event_id)\
            .single()\
            .execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket type not found"
            )

        if existing.data["quantity_sold"] > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete a ticket type that has already sold tickets. Deactivate it instead."
            )

        supabase.table("ticket_types")\
            .delete()\
            .eq("id", ticket_type_id)\
            .execute()
