from app.core.supabase import supabase
from fastapi import UploadFile

async def upload_event_image(file: UploadFile, event_id: str) -> str:
    contents = await file.read()
    path = f"events/{event_id}/{file.filename}"
    
    supabase.storage.from_("event-images").upload(
        path,
        contents,
        file_options={"content-type": file.content_type}
    )
    
    return supabase.storage.from_("event-images").get_public_url(path)


async def upload_event_images(event_id: str, files: list[UploadFile]) -> list[str]:
    image_urls = []
    for file in files:
        url = await upload_event_image(file, event_id)
        image_urls.append(url)

    # Fetch existing URLs so we don't overwrite previous uploads
    result = supabase.table("events").select("image_urls").eq("id", event_id).single().execute()
    existing_urls = result.data.get("image_urls") or []

    # Merge and save back to the database
    all_urls = existing_urls + image_urls
    supabase.table("events").update({"image_urls": all_urls}).eq("id", event_id).execute()

    return all_urls