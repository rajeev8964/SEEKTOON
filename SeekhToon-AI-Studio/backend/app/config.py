import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
load_dotenv(PROJECT_DIR / ".env")

DATA_DIR = BACKEND_DIR / "data"
GENERATED_DIR = BACKEND_DIR / "generated"
MODELS_DIR = PROJECT_DIR / "models"
UPLOAD_DIR = PROJECT_DIR / "uploads"
OUTPUT_DIR = PROJECT_DIR / "outputs"
for folder in (DATA_DIR, GENERATED_DIR, MODELS_DIR, UPLOAD_DIR, OUTPUT_DIR):
    folder.mkdir(parents=True, exist_ok=True)

APP_NAME = "SeekhToon AI Studio"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
PIPER_EXE = os.getenv("PIPER_EXE", "piper")
PIPER_VOICE = os.getenv("PIPER_VOICE", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
