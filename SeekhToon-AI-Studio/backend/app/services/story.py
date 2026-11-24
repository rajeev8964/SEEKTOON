import httpx
from fastapi import HTTPException

from ..config import OLLAMA_BASE_URL, OLLAMA_MODEL
from ..models.requests import StoryRequest


async def generate_story(req: StoryRequest) -> dict:
    prompt = (
        f"Write an original child-friendly {req.language} story for age {req.age_group}. "
        f"Topic: {req.topic}. Moral: {req.moral}. Use a title, simple language, "
        "short paragraphs and a clear positive ending. Avoid frightening or harmful content."
    )
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
    except httpx.ConnectError:
        raise HTTPException(
            503, "Ollama is not reachable. Start Ollama and download the configured model."
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            exc.response.status_code, f"Ollama error: {exc.response.text[:300]}"
        )

    return {"story": data.get("response", "").strip(), "model": OLLAMA_MODEL}
