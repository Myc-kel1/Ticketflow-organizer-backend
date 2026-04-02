# ADD TO: organizer backend → app/services/scan_service.py

from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.core.supabase import supabase


class ScanService:

    @staticmethod
    def _verify_event_ownership(event_id: str, organizer_id: str) -> Dict[str, Any]:
        """Confirm this event belongs to the organizer."""
        result = supabase.table("events")\
            .select("id, title, capacity")\
            .eq("id", event_id)\
            .eq("organizer_id", organizer_id)\
            .single()\
            .execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found or you do not have permission to access it"
            )
        return result.data

    @staticmethod
    def scan_ticket(event_id: str, ticket_id: str, organizer_id: str) -> Dict[str, Any]:
        """
        Validate and check in a ticket by scanning its QR code.
        The QR code encodes: TICKET_ID:EVENT_ID
        The scanner extracts ticket_id and passes it here.
        """
        # Verify organizer owns this event
        event = ScanService._verify_event_ownership(event_id, organizer_id)

        # Look up the ticket
        ticket_result = supabase.table("tickets")\
            .select("*, customer_profiles(full_name, email)")\
            .eq("id", ticket_id)\
            .eq("event_id", event_id)\
            .single()\
            .execute()

        if not ticket_result.data:
            return {
                "valid": False,
                "ticket_id": ticket_id,
                "message": "Ticket not found for this event. It may belong to a different event or does not exist.",
                "event_title": event["title"]
            }

        ticket = ticket_result.data
        profile = ticket.pop("customer_profiles", {}) or {}
        attendee_name = profile.get("full_name") or ticket.get("customer_email", "Unknown")
        attendee_email = ticket.get("customer_email")

        if ticket["status"] == "used":
            return {
                "valid": False,
                "ticket_id": ticket_id,
                "message": f"Ticket already used — checked in at {ticket.get('checked_in_at', 'unknown time')}",
                "attendee_name": attendee_name,
                "attendee_email": attendee_email,
                "ticket_type": ticket.get("ticket_type_name"),
                "event_title": event["title"],
                "checked_in_at": ticket.get("checked_in_at")
            }

        if ticket["status"] == "cancelled":
            return {
                "valid": False,
                "ticket_id": ticket_id,
                "message": "This ticket has been cancelled and is no longer valid.",
                "attendee_name": attendee_name,
                "event_title": event["title"]
            }

        # Valid — mark as used
        now = datetime.now(timezone.utc).isoformat()
        supabase.table("tickets").update({
            "status": "used",
            "checked_in_at": now
        }).eq("id", ticket_id).execute()

        return {
            "valid": True,
            "ticket_id": ticket_id,
            "message": "Valid ticket — check-in successful!",
            "attendee_name": attendee_name,
            "attendee_email": attendee_email,
            "ticket_type": ticket.get("ticket_type_name"),
            "event_title": event["title"],
            "checked_in_at": now
        }

    @staticmethod
    def get_event_stats(event_id: str, organizer_id: str) -> Dict[str, Any]:
        """Get ticket sales and check-in stats for a specific event."""
        event = ScanService._verify_event_ownership(event_id, organizer_id)

        # Fetch all tickets for this event
        tickets_result = supabase.table("tickets")\
            .select("id, status, ticket_type_name")\
            .eq("event_id", event_id)\
            .execute()

        tickets = tickets_result.data or []
        tickets_sold = len(tickets)
        tickets_checked_in = sum(1 for t in tickets if t["status"] == "used")
        tickets_active = sum(1 for t in tickets if t["status"] == "active")

        # Fetch revenue from paid orders
        orders_result = supabase.table("orders")\
            .select("amount, quantity")\
            .eq("event_id", event_id)\
            .eq("status", "paid")\
            .execute()

        total_revenue = sum(float(o["amount"]) for o in (orders_result.data or []))
        check_in_rate = round((tickets_checked_in / tickets_sold * 100), 1) if tickets_sold > 0 else 0.0

        # Ticket type breakdown
        type_counts: Dict[str, Dict] = {}
        for t in tickets:
            name = t.get("ticket_type_name") or "General"
            if name not in type_counts:
                type_counts[name] = {"name": name, "sold": 0, "checked_in": 0}
            type_counts[name]["sold"] += 1
            if t["status"] == "used":
                type_counts[name]["checked_in"] += 1

        # Merge with ticket type capacity data
        tt_result = supabase.table("ticket_types")\
            .select("name, quantity_available, quantity_sold, price")\
            .eq("event_id", event_id)\
            .execute()

        for tt in (tt_result.data or []):
            name = tt["name"]
            if name in type_counts:
                type_counts[name]["quantity_available"] = tt["quantity_available"]
                type_counts[name]["price"] = float(tt["price"])
            else:
                type_counts[name] = {
                    "name": name,
                    "sold": tt["quantity_sold"],
                    "checked_in": 0,
                    "quantity_available": tt["quantity_available"],
                    "price": float(tt["price"])
                }

        capacity = event.get("capacity")
        sold_out = (tickets_sold >= capacity) if capacity else False

        return {
            "event_id": event_id,
            "event_title": event["title"],
            "total_capacity": capacity,
            "tickets_sold": tickets_sold,
            "tickets_checked_in": tickets_checked_in,
            "tickets_active": tickets_active,
            "total_revenue": total_revenue,
            "check_in_rate": check_in_rate,
            "sold_out": sold_out,
            "ticket_type_breakdown": list(type_counts.values())
        }

    @staticmethod
    def get_event_attendees(event_id: str, organizer_id: str) -> Dict[str, Any]:
        """Get all attendees (ticket holders) for an event."""
        ScanService._verify_event_ownership(event_id, organizer_id)

        result = supabase.table("tickets")\
            .select("id, status, ticket_type_name, checked_in_at, created_at, customer_email, customer_profiles(full_name)")\
            .eq("event_id", event_id)\
            .order("created_at", desc=True)\
            .execute()

        attendees = []
        for t in (result.data or []):
            profile = t.pop("customer_profiles", {}) or {}
            attendees.append({
                "ticket_id": t["id"],
                "attendee_name": profile.get("full_name") or t.get("customer_email", "Unknown"),
                "attendee_email": t.get("customer_email"),
                "ticket_type": t.get("ticket_type_name"),
                "status": t["status"],
                "checked_in_at": t.get("checked_in_at"),
                "purchased_at": t["created_at"]
            })

        checked_in = sum(1 for a in attendees if a["status"] == "used")
        pending = sum(1 for a in attendees if a["status"] == "active")

        return {
            "attendees": attendees,
            "total": len(attendees),
            "checked_in": checked_in,
            "pending": pending
        }

    @staticmethod
    def get_event_orders(event_id: str, organizer_id: str) -> Dict[str, Any]:
        """Get all orders placed for an event."""
        ScanService._verify_event_ownership(event_id, organizer_id)

        result = supabase.table("orders")\
            .select("*, ticket_types(name), customer_profiles(full_name, email)")\
            .eq("event_id", event_id)\
            .order("created_at", desc=True)\
            .execute()

        orders = []
        total_revenue = 0.0

        for o in (result.data or []):
            tt = o.pop("ticket_types", {}) or {}
            profile = o.pop("customer_profiles", {}) or {}

            # Fetch tickets for this order
            tickets_res = supabase.table("tickets")\
                .select("id, status, ticket_type_name")\
                .eq("order_id", o["id"])\
                .execute()

            amount = float(o.get("amount", 0))
            if o.get("status") == "paid":
                total_revenue += amount

            orders.append({
                "id": o["id"],
                "reference": o["reference"],
                "customer_email": o.get("customer_email") or profile.get("email"),
                "customer_name": profile.get("full_name"),
                "quantity": o["quantity"],
                "amount": amount,
                "status": o["status"],
                "ticket_type": tt.get("name"),
                "created_at": o["created_at"],
                "tickets": tickets_res.data or []
            })

        return {
            "orders": orders,
            "total": len(orders),
            "total_revenue": total_revenue
        }

    @staticmethod
    def get_all_tickets(organizer_id: str) -> Dict[str, Any]:
        """Get all tickets across all of the organizer's events."""
        # First get all event IDs belonging to this organizer
        events_result = supabase.table("events")\
            .select("id, title")\
            .eq("organizer_id", organizer_id)\
            .execute()

        event_ids = [e["id"] for e in (events_result.data or [])]
        event_map = {e["id"]: e["title"] for e in (events_result.data or [])}

        if not event_ids:
            return {"tickets": [], "total": 0}

        # Fetch all tickets for those events
        result = supabase.table("tickets")\
            .select("*, customer_profiles(full_name)")\
            .in_("event_id", event_ids)\
            .order("created_at", desc=True)\
            .execute()

        tickets = []
        for t in (result.data or []):
            profile = t.pop("customer_profiles", {}) or {}
            tickets.append({
                "id": t["id"],
                "event_id": t["event_id"],
                "event_title": event_map.get(t["event_id"]),
                "order_id": t.get("order_id"),
                "customer_email": t.get("customer_email"),
                "customer_name": profile.get("full_name"),
                "ticket_type": t.get("ticket_type_name"),
                "status": t["status"],
                "qr_code_url": t.get("qr_code_url"),
                "checked_in_at": t.get("checked_in_at"),
                "created_at": t["created_at"]
            })

        return {"tickets": tickets, "total": len(tickets)}

    @staticmethod
    def get_ticket_by_id(ticket_id: str, organizer_id: str) -> Dict[str, Any]:
        """Get a single ticket — organizer must own the event it belongs to."""
        result = supabase.table("tickets")\
            .select("*, events(title, organizer_id), customer_profiles(full_name)")\
            .eq("id", ticket_id)\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        ticket = result.data
        event = ticket.pop("events", {}) or {}
        profile = ticket.pop("customer_profiles", {}) or {}

        # Verify organizer owns the event this ticket belongs to
        if event.get("organizer_id") != organizer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this ticket"
            )

        return {
            "id": ticket["id"],
            "event_id": ticket["event_id"],
            "event_title": event.get("title"),
            "order_id": ticket.get("order_id"),
            "customer_email": ticket.get("customer_email"),
            "customer_name": profile.get("full_name"),
            "ticket_type": ticket.get("ticket_type_name"),
            "status": ticket["status"],
            "qr_code_url": ticket.get("qr_code_url"),
            "checked_in_at": ticket.get("checked_in_at"),
            "created_at": ticket["created_at"]
        }
