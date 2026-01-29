from app.core.supabase import supabase
from fastapi import UploadFile

def upload_event_image(file: UploadFile, event_id: str):
    path = f"events/{event_id}/{file.filename}"
    supabase.storage.from_("event-images").upload(
        path, file.file, file_options={"content-type": file.content_type}
    )
    return supabase.storage.from_("event-images").get_public_url(path)
