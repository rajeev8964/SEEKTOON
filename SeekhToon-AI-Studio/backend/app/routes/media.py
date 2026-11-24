import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..config import MAX_UPLOAD_MB, UPLOAD_DIR
from ..models.requests import VideoRequest, VoiceRequest
from ..services.media import create_video, generate_image, generate_voice

router = APIRouter(prefix="/api")


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    allowed = {".png", ".jpg", ".jpeg", ".webp"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, "Only PNG, JPG, JPEG and WEBP images are allowed.")

    content = await file.read(MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {MAX_UPLOAD_MB} MB limit.")

    name = f"{uuid.uuid4().hex}{suffix}"
    (UPLOAD_DIR / name).write_bytes(content)
    return {
        "filename": name,
        "url": f"/uploads/{name}",
        "message": "Upload successful. This is a preview/upload endpoint, not AI editing.",
    }


@router.post("/voice")
def voice(req: VoiceRequest):
    return generate_voice(req)


@router.post("/video")
def video(req: VideoRequest):
    return create_video(req)


@router.post("/image/generate")
async def image(payload: dict):
    prompt = str(payload.get("prompt", "")).strip()
    return await generate_image(prompt)
