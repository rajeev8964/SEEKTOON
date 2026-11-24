from pathlib import Path
import subprocess, uuid, shutil
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .config import *
from .database import connect, init_db

app = FastAPI(title=APP_NAME, version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

@app.on_event("startup")
def startup():
    init_db()

class StoryRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=300)
    age_group: str = "5-10 years"
    moral: str = "Be kind and honest"
    language: str = "Hindi"

class CharacterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=3, max_length=1000)
    style: str = "2D cartoon"

class VoiceRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    voice_model: str | None = None

class VideoRequest(BaseModel):
    image_paths: list[str] = Field(min_length=1)
    audio_path: str | None = None
    seconds_per_image: int = Field(default=4, ge=1, le=20)

@app.get("/api/health")
def health():
    return {"status": "ok", "app": APP_NAME, "ollama_model": OLLAMA_MODEL}

@app.post("/api/story")
async def generate_story(req: StoryRequest):
    prompt = (
        f"Write an original child-friendly {req.language} story for age {req.age_group}. "
        f"Topic: {req.topic}. Moral: {req.moral}. Use a title, simple language, "
        "short paragraphs and a clear positive ending. Avoid frightening or harmful content."
    )
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
            )
            response.raise_for_status()
            data = response.json()
        return {"story": data.get("response", "").strip(), "model": OLLAMA_MODEL}
    except httpx.ConnectError:
        raise HTTPException(503, "Ollama is not reachable. Start Ollama and download the configured model.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(exc.response.status_code, f"Ollama error: {exc.response.text[:300]}")

@app.get("/api/characters")
def list_characters():
    with connect() as db:
        rows = db.execute("SELECT * FROM characters ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]

@app.post("/api/characters")
def create_character(req: CharacterRequest):
    with connect() as db:
        cur = db.execute(
            "INSERT INTO characters(name, description, style) VALUES (?, ?, ?)",
            (req.name, req.description, req.style)
        )
        row = db.execute("SELECT * FROM characters WHERE id=?", (cur.lastrowid,)).fetchone()
    return dict(row)

@app.delete("/api/characters/{character_id}")
def delete_character(character_id: int):
    with connect() as db:
        cur = db.execute("DELETE FROM characters WHERE id=?", (character_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Character not found")
    return {"deleted": character_id}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    allowed = {".png", ".jpg", ".jpeg", ".webp"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, "Only PNG, JPG, JPEG and WEBP images are allowed.")
    content = await file.read()
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {MAX_UPLOAD_MB} MB limit.")
    name = f"{uuid.uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / name
    destination.write_bytes(content)
    return {"filename": name, "url": f"/uploads/{name}", "message": "Upload successful. This is a preview/upload endpoint, not AI editing."}

@app.post("/api/voice")
def generate_voice(req: VoiceRequest):
    voice = req.voice_model or PIPER_VOICE
    if not voice:
        raise HTTPException(503, "Set PIPER_VOICE to a downloaded Piper voice model (.onnx) in backend/.env.")
    if not shutil.which(PIPER_EXE) and not Path(PIPER_EXE).exists():
        raise HTTPException(503, "Piper executable not found. Install Piper and set PIPER_EXE.")
    output_name = f"{uuid.uuid4().hex}.wav"
    output_path = OUTPUT_DIR / output_name
    try:
        subprocess.run(
            [PIPER_EXE, "--model", voice, "--output_file", str(output_path)],
            input=req.text, text=True, check=True, capture_output=True, timeout=120
        )
    except subprocess.CalledProcessError as exc:
        raise HTTPException(500, f"Piper failed: {exc.stderr[-500:]}")
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Voice generation timed out.")
    return {"audio_url": f"/outputs/{output_name}", "filename": output_name}

@app.post("/api/video")
def create_video(req: VideoRequest):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise HTTPException(503, "FFmpeg is not installed or not on PATH.")
    paths = []
    for item in req.image_paths:
        candidate = (UPLOAD_DIR / Path(item).name).resolve()
        if not candidate.exists():
            raise HTTPException(404, f"Image not found: {Path(item).name}")
        paths.append(candidate)
    list_file = OUTPUT_DIR / f"{uuid.uuid4().hex}.txt"
    output_name = f"{uuid.uuid4().hex}.mp4"
    output_path = OUTPUT_DIR / output_name
    with list_file.open("w", encoding="utf-8") as f:
        for path in paths:
            f.write(f"file '{path.as_posix()}'\n")
            f.write(f"duration {req.seconds_per_image}\n")
        f.write(f"file '{paths[-1].as_posix()}'\n")
    cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
           "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
           "-r", "25"]
    if req.audio_path:
        audio = (OUTPUT_DIR / Path(req.audio_path).name).resolve()
        if not audio.exists():
            raise HTTPException(404, "Audio file not found.")
        cmd += ["-i", str(audio), "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", str(output_path)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
    except subprocess.CalledProcessError as exc:
        raise HTTPException(500, f"FFmpeg failed: {exc.stderr.decode(errors='ignore')[-700:]}")
    finally:
        list_file.unlink(missing_ok=True)
    return {"video_url": f"/outputs/{output_name}", "filename": output_name}

@app.post("/api/image/generate")
async def generate_image(payload: dict):
    if not HF_TOKEN or not HF_IMAGE_MODEL:
        raise HTTPException(503, "Configure HF_TOKEN and HF_IMAGE_MODEL in backend/.env to enable image generation.")
    prompt = str(payload.get("prompt", "")).strip()
    if len(prompt) < 5 or len(prompt) > 1000:
        raise HTTPException(400, "Prompt must contain 5 to 1000 characters.")
    url = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(url, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json={"inputs": prompt})
    if response.status_code != 200:
        raise HTTPException(response.status_code, f"Image provider error: {response.text[:300]}")
    name = f"{uuid.uuid4().hex}.png"
    (OUTPUT_DIR / name).write_bytes(response.content)
    return {"image_url": f"/outputs/{name}", "filename": name}
