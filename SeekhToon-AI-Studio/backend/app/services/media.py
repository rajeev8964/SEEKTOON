import shutil
import subprocess
import uuid
from pathlib import Path

import httpx
from fastapi import HTTPException

from ..config import (
    HF_IMAGE_MODEL,
    HF_TOKEN,
    OUTPUT_DIR,
    PIPER_EXE,
    PIPER_VOICE,
    UPLOAD_DIR,
)
from ..models.requests import VideoRequest, VoiceRequest


def generate_voice(req: VoiceRequest) -> dict:
    voice = req.voice_model or PIPER_VOICE
    if not voice:
        raise HTTPException(
            503, "Set PIPER_VOICE to a downloaded Piper voice model (.onnx) in .env."
        )
    if not shutil.which(PIPER_EXE) and not Path(PIPER_EXE).exists():
        raise HTTPException(503, "Piper executable not found. Install Piper and set PIPER_EXE.")

    output_name = f"{uuid.uuid4().hex}.wav"
    output_path = OUTPUT_DIR / output_name
    try:
        subprocess.run(
            [PIPER_EXE, "--model", voice, "--output_file", str(output_path)],
            input=req.text,
            text=True,
            check=True,
            capture_output=True,
            timeout=120,
        )
    except subprocess.CalledProcessError as exc:
        raise HTTPException(500, f"Piper failed: {exc.stderr[-500:]}")
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Voice generation timed out.")
    return {"audio_url": f"/outputs/{output_name}", "filename": output_name}


def create_video(req: VideoRequest) -> dict:
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
    with list_file.open("w", encoding="utf-8") as file:
        for path in paths:
            file.write(f"file '{path.as_posix()}'\n")
            file.write(f"duration {req.seconds_per_image}\n")
        file.write(f"file '{paths[-1].as_posix()}'\n")

    command = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-vf",
        "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-r",
        "25",
    ]
    if req.audio_path:
        audio = (OUTPUT_DIR / Path(req.audio_path).name).resolve()
        if not audio.exists():
            list_file.unlink(missing_ok=True)
            raise HTTPException(404, "Audio file not found.")
        command += ["-i", str(audio), "-shortest"]
    command += ["-c:v", "libx264", "-pix_fmt", "yuv420p", str(output_path)]

    try:
        subprocess.run(command, check=True, capture_output=True, timeout=300)
    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            500, f"FFmpeg failed: {exc.stderr.decode(errors='ignore')[-700:]}"
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Video generation timed out.")
    finally:
        list_file.unlink(missing_ok=True)

    return {"video_url": f"/outputs/{output_name}", "filename": output_name}


async def generate_image(prompt: str) -> dict:
    if not HF_TOKEN or not HF_IMAGE_MODEL:
        raise HTTPException(
            503, "Configure HF_TOKEN and HF_IMAGE_MODEL in .env to enable image generation."
        )
    if len(prompt) < 5 or len(prompt) > 1000:
        raise HTTPException(400, "Prompt must contain 5 to 1000 characters.")

    url = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": prompt},
        )
    if response.status_code != 200:
        raise HTTPException(
            response.status_code, f"Image provider error: {response.text[:300]}"
        )

    name = f"{uuid.uuid4().hex}.png"
    (OUTPUT_DIR / name).write_bytes(response.content)
    return {"image_url": f"/outputs/{name}", "filename": name}
