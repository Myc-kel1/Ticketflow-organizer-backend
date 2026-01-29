from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional
from datetime import date

from app.schemas.sales import SalesReport, DailySales
from app.services.sales_service import get_sales
from app.dependencies.permissions import require_organizer


router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("/report")
async def get_sales_report(
    current_user: Dict[str, Any] = Depends(require_organizer),
    event_id: Optional[str] = Query(None, description="Filter by specific event")
):
    
    if event_id:
        report = get_sales.get_event_sales_report(
            event_id=event_id,
            organizer_id=current_user["user_id"]
        )
        return SalesReport(**report)
    else:
        reports = get_sales.get_all_sales_reports(
            organizer_id=current_user["user_id"]
        )
        return {"sales_reports": [SalesReport(**r) for r in reports]}


@router.get("/daily")
async def get_daily_sales(
    current_user: Dict[str, Any] = Depends(require_organizer),
    event_id: Optional[str] = Query(None, description="Filter by event"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date")
):
    
    daily_sales = get_sales.get_daily_sales(
        organizer_id=current_user["user_id"],
        event_id=event_id,
        start_date=start_date,
        end_date=end_date
    )
    return {"daily_sales": [DailySales(**s) for s in daily_sales]}


@router.get("/summary")
async def get_sales_summary(
    current_user: Dict[str, Any] = Depends(require_organizer)
):
    
    summary = get_sales.get_sales_summary(
        organizer_id=current_user["user_id"]
    )
    return summary