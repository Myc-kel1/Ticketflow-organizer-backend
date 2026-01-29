from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.schemas.dashboard import DashboardStats, RecentActivity
from app.services.dashboard_service import EventService
from app.dependencies.permissions import require_organizer


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: Dict[str, Any] = Depends(require_organizer)
) -> DashboardStats:

    stats = EventService.get_organizer_stats(
        organizer_id=current_user["user_id"]
    )
    return DashboardStats(**stats)


@router.get("/recent-activity")
async def get_recent_activity(
    current_user: Dict[str, Any] = Depends(require_organizer),
    limit: int = 10
):
    
    activities = EventService.get_recent_activity(
        organizer_id=current_user["user_id"],
        limit=limit
    )
    return {"activities": activities}


@router.get("/revenue-breakdown")
async def get_revenue_breakdown(
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    breakdown = EventService.get_revenue_breakdown(
        organizer_id=current_user["user_id"]
    )
    return {"revenue_breakdown": breakdown}