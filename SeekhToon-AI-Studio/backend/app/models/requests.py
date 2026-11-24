from pydantic import BaseModel, Field


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
