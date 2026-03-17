
from pydantic import BaseModel


class VideoCreate(BaseModel):
    video_url: str
