from pydantic import BaseModel, Field
from typing import Optional


class DashboardStats(BaseModel):
    """Dashboard statistics schema"""
    total_events: int = Field(..., description="Total number of events")
    upcoming_events: int = Field(..., description="Number of upcoming events")
    past_events: int = Field(..., description="Number of past events")
    total_tickets_sold: int = Field(..., description="Total tickets sold across all events")
    total_revenue: float = Field(..., description="Total revenue generated")
    active_attendees: int = Field(..., description="Number of unique active attendees")


class RecentActivity(BaseModel):
    """Recent activity schema"""
    event_id: str = Field(..., description="Event ID")
    event_title: str = Field(..., description="Event title")
    activity_type: str = Field(..., description="Type of activity (e.g., ticket_purchase, check_in)")
    description: str = Field(..., description="Activity description")
    timestamp: str = Field(..., description="Activity timestamp")


class RevenueBreakdownItem(BaseModel):
    """Revenue breakdown per event"""
    event_id: str
    event_title: str
    tickets_sold: int
    revenue: float
    ticket_price: float


class DashboardResponse(BaseModel):
    """Complete dashboard response"""
    stats: DashboardStats
    recent_activities: list[RecentActivity] = []
    revenue_breakdown: list[RevenueBreakdownItem] = []