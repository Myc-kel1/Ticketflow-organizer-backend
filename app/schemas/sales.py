from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class SalesReport(BaseModel):
    """Sales report schema for a single event"""
    event_id: str
    event_title: str
    total_tickets_sold: int = Field(..., description="Total tickets sold")
    total_revenue: float = Field(..., description="Total revenue generated")
    tickets_available: Optional[int] = Field(None, description="Remaining tickets (if capacity set)")
    average_ticket_price: float = Field(..., description="Average price per ticket")


class DailySales(BaseModel):
    """Daily sales breakdown schema"""
    sale_date: date = Field(..., description="Sale date")
    tickets_sold: int = Field(..., description="Tickets sold on this day")
    revenue: float = Field(..., description="Revenue generated on this day")


class SalesSummary(BaseModel):
    """Overall sales summary for all events"""
    total_tickets_sold: int = Field(..., description="Total tickets sold across all events")
    total_revenue: float = Field(..., description="Total revenue across all events")
    total_events: int = Field(..., description="Total number of events")
    average_tickets_per_event: float = Field(..., description="Average tickets sold per event")
    average_revenue_per_event: float = Field(..., description="Average revenue per event")


class SalesReportListResponse(BaseModel):
    """List of sales reports"""
    sales_reports: list[SalesReport]
    total_events: int
    combined_revenue: float


class DailySalesResponse(BaseModel):
    """Daily sales response"""
    daily_sales: list[DailySales]
    total_days: int
    total_revenue: float
    total_tickets: int


class MonthlyRevenue(BaseModel):
    """Monthly revenue breakdown"""
    year: int
    month: int
    revenue: float
    tickets_sold: int


class RevenueByCategory(BaseModel):
    """Revenue breakdown by event category"""
    category: str
    revenue: float
    tickets_sold: int
    events_count: int