from typing import Dict, Any, List
from fastapi import HTTPException, status
from datetime import datetime

from app.core.supabase import supabase


class ScannerService:
    """Service layer for ticket scanning and check-in operations"""
    
    @staticmethod
    def check_in_ticket(ticket_code: str, organizer_id: str) -> Dict[str, Any]:
        """Check in a ticket using its unique code."""
        try:
            # Get ticket by code
            response = (
                supabase.table("tickets")
                .select("*, events!inner(organizer_id, title, start_date)")
                .eq("ticket_code", ticket_code)
                .execute()
            )
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invalid ticket code"
                )
            
            ticket = response.data[0]
            
            # Verify organizer owns the event
            if ticket["events"]["organizer_id"] != organizer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to check in this ticket"
                )
            
            # Check if ticket is cancelled
            if ticket["status"] == "cancelled":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ticket has been cancelled"
                )
            
            # Check if already checked in
            if ticket["status"] == "checked_in":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ticket already checked in at {ticket.get('checked_in_at')}"
                )
            
            # Perform check-in
            now = datetime.utcnow().isoformat()
            update_response = (
                supabase.table("tickets")
                .update({
                    "status": "checked_in",
                    "checked_in_at": now
                })
                .eq("ticket_code", ticket_code)
                .execute()
            )
            
            if not update_response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to check in ticket"
                )
            
            return {
                "success": True,
                "message": "Ticket checked in successfully",
                "ticket_id": ticket["id"],
                "attendee_name": ticket.get("attendee_name", "N/A"),
                "attendee_email": ticket.get("attendee_email", "N/A"),
                "event_title": ticket["events"]["title"],
                "checked_in_at": now
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Check-in failed: {str(e)}"
            )
    
    @staticmethod
    def validate_ticket(ticket_code: str, organizer_id: str) -> Dict[str, Any]:
        """Validate a ticket without checking it in."""
        try:
            # Get ticket by code
            response = (
                supabase.table("tickets")
                .select("*, events!inner(organizer_id, title, start_date)")
                .eq("ticket_code", ticket_code)
                .execute()
            )
            
            if not response.data:
                return {
                    "valid": False,
                    "message": "Invalid ticket code",
                    "ticket_id": None,
                    "attendee_name": None,
                    "attendee_email": None,
                    "event_title": None,
                    "event_date": None,
                    "already_checked_in": False
                }
            
            ticket = response.data[0]
            
            # Verify organizer owns the event
            if ticket["events"]["organizer_id"] != organizer_id:
                return {
                    "valid": False,
                    "message": "Not authorized for this event",
                    "ticket_id": ticket["id"],
                    "attendee_name": None,
                    "attendee_email": None,
                    "event_title": None,
                    "event_date": None,
                    "already_checked_in": False
                }
            
            # Check ticket status
            if ticket["status"] == "cancelled":
                return {
                    "valid": False,
                    "message": "Ticket has been cancelled",
                    "ticket_id": ticket["id"],
                    "attendee_name": ticket.get("attendee_name"),
                    "attendee_email": ticket.get("attendee_email"),
                    "event_title": ticket["events"]["title"],
                    "event_date": ticket["events"]["start_date"],
                    "already_checked_in": False
                }
            
            already_checked_in = ticket["status"] == "checked_in"
            
            return {
                "valid": True,
                "ticket_id": ticket["id"],
                "attendee_name": ticket.get("attendee_name", "N/A"),
                "attendee_email": ticket.get("attendee_email", "N/A"),
                "event_title": ticket["events"]["title"],
                "event_date": ticket["events"]["start_date"],
                "already_checked_in": already_checked_in,
                "checked_in_at": ticket.get("checked_in_at"),
                "message": "Ticket is valid" if not already_checked_in else "Already checked in"
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Validation failed: {str(e)}"
            )
    
    @staticmethod
    def get_event_checkins(event_id: str, organizer_id: str) -> List[Dict[str, Any]]:
        """Get all checked-in tickets for an event."""
        try:
            # Verify event ownership
            event_response = (
                supabase.table("events")
                .select("*")
                .eq("id", event_id)
                .execute()
            )
            
            if not event_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found"
                )
            
            if event_response.data[0]["organizer_id"] != organizer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access this event"
                )
            
            # Get checked-in tickets
            response = (
                supabase.table("tickets")
                .select("*")
                .eq("event_id", event_id)
                .eq("status", "checked_in")
                .order("checked_in_at", desc=True)
                .execute()
            )
            
            return response.data
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve check-ins: {str(e)}"
            )