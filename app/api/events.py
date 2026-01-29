from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from typing import List, Dict, Any, Optional
import json

from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.services.event_service import EventService
from app.services.image_service import upload_event_image
from app.schemas.images import ImageUploadResponse
from app.dependencies.permissions import require_organizer


router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event with optional images"
)
async def create_event(
    title: str = Form(...),
    location: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    description: Optional[str] = Form(None),
    capacity: Optional[int] = Form(None),
    ticket_price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    images: List[UploadFile] = File(None),
    current_user: Dict[str, Any] = Depends(require_organizer)
) -> EventResponse:
    
    # Create event data object
    event_data = EventCreate(
        title=title,
        description=description,
        location=location,
        start_date=start_date,
        end_date=end_date,
        capacity=capacity,
        ticket_price=ticket_price,
        category=category
    )
    
    # Create event first
    event = EventService.create_event(
        event_data=event_data,
        organizer_id=current_user["user_id"]
    )
    
    # Upload images if provided
    if images and len(images) > 0:
        try:
            image_urls = await upload_event_image.upload_event_images(
                event_id=event["id"],
                files=images
            )
            
            # Update event with image URLs
            event = EventService.update_event_images(
                event_id=event["id"],
                image_urls=image_urls
            )
        except Exception as e:
            # If image upload fails, event is still created but without images
            print(f"Image upload failed: {str(e)}")
    
    return EventResponse(**event)


@router.get(
    "/me",
    response_model=List[EventResponse],
    summary="Get my events"
)
async def get_my_events(
    current_user: Dict[str, Any] = Depends(require_organizer)
) -> List[EventResponse]:
    
    events = EventService.get_organizer_events(
        organizer_id=current_user["user_id"]
    )
    return [EventResponse(**event) for event in events]


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event by ID"
)
async def get_event(
    event_id: str,
    current_user: Dict[str, Any] = Depends(require_organizer)
) -> EventResponse:
    
    event = EventService.get_event_by_id_with_auth(
        event_id=event_id,
        user_id=current_user["user_id"]
    )
    return EventResponse(**event)


@router.patch(
    "/{event_id}",
    response_model=EventResponse,
    summary="Update an event"
)
async def update_event(
    event_id: str,
    event_data: EventUpdate,
    current_user: Dict[str, Any] = Depends(require_organizer)
) -> EventResponse:
    
    event = EventService.update_event(
        event_id=event_id,
        event_data=event_data,
        organizer_id=current_user["user_id"]
    )
    return EventResponse(**event)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an event"
)
async def delete_event(
    event_id: str,
    current_user: Dict[str, Any] = Depends(require_organizer)
) -> None:
    
    EventService.delete_event(
        event_id=event_id,
        organizer_id=current_user["user_id"]
    )


@router.post(
    "/{event_id}/images",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload event images"
)
async def upload_event_images(
    event_id: str,
    files: List[UploadFile] = File(..., description="Event images (max 10, 5MB each)"),
    current_user: Dict[str, Any] = Depends(require_organizer)
) -> ImageUploadResponse:
    
    # Verify event ownership
    EventService.verify_event_ownership(
        event_id=event_id,
        organizer_id=current_user["user_id"]
    )
    
    # Upload images
    image_urls = await upload_event_image.upload_event_images(
        event_id=event_id,
        files=files
    )
    
    return ImageUploadResponse(
        event_id=event_id,
        image_urls=image_urls
    )