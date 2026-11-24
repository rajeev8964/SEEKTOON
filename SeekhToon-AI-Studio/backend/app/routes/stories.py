from fastapi import APIRouter

from ..models.requests import StoryRequest
from ..services.story import generate_story

router = APIRouter(prefix="/api")


@router.post("/story")
async def create_story(req: StoryRequest):
    return await generate_story(req)
