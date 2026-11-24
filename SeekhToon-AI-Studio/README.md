# SeekhToon AI Studio

A starter full-stack project based on the user's 11-slide presentation. Frontend: HTML/CSS/JS. Backend: FastAPI. Local AI: Ollama and Piper. Optional image provider: Hugging Face Inference API. Video assembly: FFmpeg.

## What is implemented in this starter
- Responsive dashboard and navigation.
- Hindi story generation through a locally running Ollama model.
- Piper text-to-speech endpoint (requires Piper executable and a compatible voice model).
- Image upload and browser preview.
- Character description CRUD stored in SQLite.
- Optional Hugging Face image-generation endpoint.
- MP4 slideshow assembly from uploaded images using FFmpeg.

## Not implemented / not promised
- AI photo editing: upload currently previews the photo; no image-edit model is wired.
- Character visual consistency: descriptions are saved, but no identity-locking image model is integrated.
- Full video editor: current export is a simple image slideshow with optional narration.
- Production authentication, payments, multi-user authorization and cloud object storage.

## Requirements
Windows 11, Python 3.11+, Git (optional), Ollama for stories, Piper for voice, FFmpeg for video. For 8 GB RAM, close heavy applications while running local models.

## Local setup (PowerShell)
1. Open PowerShell and move to the folder where you extracted this repository:
   `cd path\\to\\SeekhToon-AI-Studio`
2. Create a virtual environment:
   `py -3.11 -m venv .venv`
   `.\.venv\\Scripts\\Activate.ps1`
   If script execution is blocked for this terminal only: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
3. Install backend dependencies:
   `cd backend`
   `pip install -r requirements.txt`
4. Copy environment template:
   `Copy-Item .env.example .env`
5. Start backend:
   `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
6. Open a second PowerShell terminal, go to the frontend folder and run:
   `cd path\\to\\SeekhToon-AI-Studio\\frontend`
   `py -m http.server 5500`
7. Open `http://127.0.0.1:5500`.

## Ollama story setup
Install Ollama for Windows from https://ollama.com/download/windows. Then:
`ollama pull qwen2.5:3b`
Check:
`ollama list`
The API defaults to `http://127.0.0.1:11434` and model `qwen2.5:3b`. Change `OLLAMA_BASE_URL` or `OLLAMA_MODEL` in `backend/.env` if needed.

## Piper voice setup
Install Piper using its current official distribution for your OS and download a Hindi voice model plus its matching `.onnx.json` config. Set `PIPER_EXE` to the executable path and `PIPER_VOICE` to the `.onnx` model path in `backend/.env`. Restart FastAPI. Voice availability depends on the selected Hindi model.

## FFmpeg
Install FFmpeg and ensure `ffmpeg` is available on PATH. Verify with `ffmpeg -version`. Upload images through Photo Editor first; copy the returned filename(s) into Video Generator separated by commas. Optionally enter the WAV filename returned by Voice Studio.

## Optional image generation
Set `HF_TOKEN` and `HF_IMAGE_MODEL` in `backend/.env`. Keep tokens private; never place API keys in frontend JavaScript or commit `.env`. Provider access, model availability, quotas and billing can change. Restart backend after changing environment variables.

## API docs
With backend running: `http://127.0.0.1:8000/docs`
Health check: `http://127.0.0.1:8000/api/health`

## Online deployment outline
This application has local AI dependencies that are not automatically available on typical web hosts. For a public deployment:
- Deploy the FastAPI backend to a Python-capable host (Render or equivalent).
- Deploy `frontend/` as a static site (Render Static Site, Cloudflare Pages, or equivalent).
- Set the frontend API base URL by opening browser dev tools and running:
  `localStorage.setItem("seekhtoon_api","https://YOUR-BACKEND-DOMAIN")`
  then reload. For a permanent public release, replace this temporary setting with a build-time config.
- Configure backend environment variables in the host dashboard, not in source code.
- Set `OLLAMA_BASE_URL` to a reachable secured remote Ollama service; `127.0.0.1` on a cloud host refers to that host itself and will not reach your laptop.
- Use a persistent disk or managed database/object storage for production. The included SQLite database and local folders are suitable for local development, not reliable multi-instance production storage.
- Restrict CORS to your actual frontend domain before public release. Add authentication, rate limiting, file scanning, upload quotas and HTTPS before allowing public users.
- Do not expose an unauthenticated Ollama endpoint publicly.

## Troubleshooting
- `Ollama is not reachable`: launch Ollama and test `http://127.0.0.1:11434`; run `ollama list`.
- Story model not found: run `ollama pull qwen2.5:3b`.
- Piper not found: check `PIPER_EXE` and `PIPER_VOICE` paths.
- FFmpeg not found: install it, reopen terminal and run `ffmpeg -version`.
- Browser network error: verify backend is running on port 8000 and frontend API URL is correct.
