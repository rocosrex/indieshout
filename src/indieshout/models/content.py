from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ContentType(str, Enum):
    BLOG = "blog"
    SNS = "sns"


class Content(BaseModel):
    content_type: ContentType
    text: str
    title: str | None = None
    image_paths: list[str] | None = None
    video_path: str | None = None
    tags: list[str] | None = None
    platforms: list[str] = []
    sns_text: str | None = None
    scheduled_at: datetime | None = None
