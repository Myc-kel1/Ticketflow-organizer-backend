from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from datetime import datetime

from app.core.supabase import supabase
from app.schemas.event import EventCreate, EventUpdate


class EventService:
    """Service layer for event database operations"""
    
    @staticmethod
    def create_event(event_data: EventCreate, organizer_id: str) -> Dict[str, Any]:
        """Create a new event in the database."""
        try:
            # Validate date logic
            if event_data.end_date <= event_data.start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be after start date"
                )
            
            event_dict = event_data.model_dump()
            event_dict["organizer_id"] = organizer_id
            event_dict["created_at"] = datetime.utcnow().isoformat()
            
            response = supabase.table("events").insert(event_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create event"
                )
            
            return response.data[0]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
    
    @staticmethod
    def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve event by ID."""
        try:
            response = supabase.table("events").select("*").eq("id", event_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
    
    @staticmethod
    def get_event_by_id_with_auth(event_id: str, user_id: str) -> Dict[str, Any]:
        """Get event by ID with authorization check."""
        event = EventService.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        if event["organizer_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this event"
            )
        
        return event
    
    @staticmethod
    def get_organizer_events(organizer_id: str) -> List[Dict[str, Any]]:
        """Get all events created by a specific organizer."""
        try:
            response = (
                supabase.table("events")
                .select("*")
                .eq("organizer_id", organizer_id)
                .order("created_at", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
    
    @staticmethod
    def update_event(
        event_id: str, 
        event_data: EventUpdate, 
        organizer_id: str
    ) -> Dict[str, Any]:
        """Update an existing event."""
        try:
            # Check if event exists and belongs to organizer
            existing_event = EventService.get_event_by_id(event_id)
            if not existing_event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found"
                )
            
            if existing_event["organizer_id"] != organizer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to update this event"
                )
            
            # Only update fields that were provided
            update_dict = event_data.model_dump(exclude_unset=True)
            
            if not update_dict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )
            
            # Validate dates if both are being updated
            if "start_date" in update_dict and "end_date" in update_dict:
                if update_dict["end_date"] <= update_dict["start_date"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="End date must be after start date"
                    )
            
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            response = (
                supabase.table("events")
                .update(update_dict)
                .eq("id", event_id)
                .execute()
            )
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update event"
                )
            
            return response.data[0]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
    
    @staticmethod
    def delete_event(event_id: str, organizer_id: str) -> None:
        """Delete an event."""
        try:
            # Check if event exists and belongs to organizer
            existing_event = EventService.get_event_by_id(event_id)
            if not existing_event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found"
                )
            
            if existing_event["organizer_id"] != organizer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this event"
                )
            
            response = supabase.table("events").delete().eq("id", event_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete event"
                )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
    
    @staticmethod
    def verify_event_ownership(event_id: str, organizer_id: str) -> None:
        """Verify that an organizer owns an event."""
        event = EventService.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        if event["organizer_id"] != organizer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this event"
            )