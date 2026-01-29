from app.core.supabase import supabase


def get_sales(event_id: str, organizer_id: str):
    return (
        supabase.table("ticket_sales")
        .select("*")
        .eq("event_id", event_id)
        .eq("organizer_id", organizer_id)
        .execute()
        .data
    )


def get_attendees(event_id: str, organizer_id: str):
    return (
        supabase.table("attendees")
        .select("*")
        .eq("event_id", event_id)
        .eq("organizer_id", organizer_id)
        .execute()
        .data
    )