from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from datetime import date, datetime
from collections import defaultdict

from app.core.supabase import supabase
from app.services.event_service import EventService


class SalesService:
    """Service layer for sales reporting and analytics"""
    
    @staticmethod
    def get_event_sales_report(event_id: str, organizer_id: str) -> Dict[str, Any]:
        """Get sales report for a specific event."""
        try:
            # Verify event ownership and get event details
            event = EventService.get_event_by_id_with_auth(event_id, organizer_id)
            
            # Get tickets for this event
            tickets_response = (
                supabase.table("tickets")
                .select("*")
                .eq("event_id", event_id)
                .execute()
            )
            tickets = tickets_response.data
            
            # Calculate statistics
            active_tickets = [t for t in tickets if t.get("status") != "cancelled"]
            total_tickets_sold = len(active_tickets)
            total_revenue = sum(float(t.get("price", 0)) for t in active_tickets)
            
            # Calculate average ticket price
            avg_ticket_price = (
                total_revenue / total_tickets_sold 
                if total_tickets_sold > 0 
                else 0
            )
            
            # Get remaining capacity
            capacity = event.get("capacity")
            tickets_available = capacity - total_tickets_sold if capacity else None
            
            return {
                "event_id": event_id,
                "event_title": event["title"],
                "total_tickets_sold": total_tickets_sold,
                "total_revenue": total_revenue,
                "tickets_available": tickets_available,
                "average_ticket_price": avg_ticket_price
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve sales report: {str(e)}"
            )
    
    @staticmethod
    def get_all_sales_reports(organizer_id: str) -> List[Dict[str, Any]]:
        """Get sales reports for all organizer's events."""
        try:
            # Get all organizer's events
            events = EventService.get_organizer_events(organizer_id)
            
            reports = []
            for event in events:
                try:
                    report = SalesService.get_event_sales_report(
                        event_id=event["id"],
                        organizer_id=organizer_id
                    )
                    reports.append(report)
                except Exception:
                    # Skip events with errors
                    continue
            
            return reports
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve sales reports: {str(e)}"
            )
    
    @staticmethod
    def get_daily_sales(
        organizer_id: str,
        event_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get daily sales breakdown."""
        try:
            # Build query
            query = supabase.table("tickets").select("*, events!inner(organizer_id)")
            query = query.eq("events.organizer_id", organizer_id)
            
            if event_id:
                query = query.eq("event_id", event_id)
            
            if start_date:
                query = query.gte("purchased_at", start_date.isoformat())
            
            if end_date:
                query = query.lte("purchased_at", end_date.isoformat())
            
            response = query.execute()
            tickets = response.data
            
            # Group by date
            daily_data = defaultdict(lambda: {"tickets_sold": 0, "revenue": 0.0})
            
            for ticket in tickets:
                if ticket.get("status") == "cancelled":
                    continue
                
                purchase_date = datetime.fromisoformat(
                    ticket["purchased_at"].replace("Z", "+00:00")
                ).date()
                
                daily_data[purchase_date]["tickets_sold"] += 1
                daily_data[purchase_date]["revenue"] += float(ticket.get("price", 0))
            
            # Convert to list and sort
            daily_sales = [
                {
                    "date": date_key,
                    "tickets_sold": data["tickets_sold"],
                    "revenue": data["revenue"]
                }
                for date_key, data in daily_data.items()
            ]
            
            daily_sales.sort(key=lambda x: x["date"], reverse=True)
            
            return daily_sales
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve daily sales: {str(e)}"
            )
    
    @staticmethod
    def get_sales_summary(organizer_id: str) -> Dict[str, Any]:
        """Get overall sales summary for all organizer's events."""
        try:
            # Get all tickets for organizer's events
            response = (
                supabase.table("tickets")
                .select("*, events!inner(organizer_id)")
                .eq("events.organizer_id", organizer_id)
                .execute()
            )
            tickets = response.data
            
            # Filter active tickets
            active_tickets = [t for t in tickets if t.get("status") != "cancelled"]
            
            # Calculate totals
            total_tickets_sold = len(active_tickets)
            total_revenue = sum(float(t.get("price", 0)) for t in active_tickets)
            total_events = len(set(t["event_id"] for t in active_tickets))
            
            # Calculate average per event
            avg_tickets_per_event = (
                total_tickets_sold / total_events 
                if total_events > 0 
                else 0
            )
            avg_revenue_per_event = (
                total_revenue / total_events 
                if total_events > 0 
                else 0
            )
            
            return {
                "total_tickets_sold": total_tickets_sold,
                "total_revenue": total_revenue,
                "total_events": total_events,
                "average_tickets_per_event": round(avg_tickets_per_event, 2),
                "average_revenue_per_event": round(avg_revenue_per_event, 2)
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve sales summary: {str(e)}"
            )