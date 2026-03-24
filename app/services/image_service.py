from app.core.supabase import supabase
from fastapi import UploadFile

async def upload_event_image(file: UploadFile, event_id: str) -> str:
    contents = await file.read()  # read as bytes — this is the critical fix
    path = f"events/{event_id}/{file.filename}"
    
    supabase.storage.from_("event-images").upload(
        path,
        contents,  # pass bytes, not file.file
        file_options={"content-type": file.content_type}
    )
    
    return supabase.storage.from_("event-images").get_public_url(path)


async def upload_event_images(event_id: str, files: list[UploadFile]) -> list[str]:
    image_urls = []
    for file in files:
        url = await upload_event_image(file, event_id)
        image_urls.append(url)
    return image_urls