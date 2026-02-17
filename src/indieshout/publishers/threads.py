import os

import httpx

from indieshout.formatter.content_formatter import ContentFormatter
from indieshout.models.content import Content
from indieshout.publishers.base import BasePublisher

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_IMAGE_SIZE = 8 * 1024 * 1024  # 8MB
MAX_IMAGES = 10
THREADS_API_BASE = "https://graph.threads.net/v1.0"


class ThreadsPublisher(BasePublisher):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.access_token: str | None = None
        self.user_id: str | None = None
        self._formatter = ContentFormatter()

    def authenticate(self) -> bool:
        threads_config = self.config.get("threads", {})
        self.access_token = threads_config.get("access_token", "")
        self.user_id = threads_config.get("user_id", "")

        if not self.access_token or not self.user_id:
            raise ValueError("Threads access_token and user_id are required")

        # 토큰 유효성 검증 (간단히 user info 조회)
        with httpx.Client() as client:
            response = client.get(
                f"{THREADS_API_BASE}/me",
                params={"access_token": self.access_token},
            )
            if response.status_code != 200:
                raise RuntimeError(f"Authentication failed: {response.text}")

        return True

    def validate(self, content: Content) -> bool:
        if not content.text or not content.text.strip():
            raise ValueError("Text content is required")

        if not self.access_token:
            raise RuntimeError("Not authenticated. Call authenticate() first")

        if content.image_paths:
            if len(content.image_paths) > MAX_IMAGES:
                raise ValueError(
                    f"Maximum {MAX_IMAGES} images allowed, got {len(content.image_paths)}"
                )

            for path in content.image_paths:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Image not found: {path}")

                ext = os.path.splitext(path)[1].lower()
                if ext not in ALLOWED_IMAGE_EXTENSIONS:
                    raise ValueError(f"Unsupported image format: {ext}")

                size = os.path.getsize(path)
                if size > MAX_IMAGE_SIZE:
                    raise ValueError(f"Image too large ({size} bytes): {path}")

        return True

    def format_content(self, content: Content) -> dict:
        text = self._formatter._format_threads(content)
        return {"text": text}

    def publish(self, content: Content) -> dict:
        formatted = self.format_content(content)

        with httpx.Client(timeout=30.0) as client:
            # 텍스트만 게시
            if not content.image_paths:
                # 1. Create container
                create_response = client.post(
                    f"{THREADS_API_BASE}/{self.user_id}/threads",
                    data={
                        "media_type": "TEXT",
                        "text": formatted["text"],
                        "access_token": self.access_token,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if create_response.status_code != 200:
                    raise RuntimeError(
                        f"Failed to create thread container: {create_response.text}"
                    )

                container_id = create_response.json().get("id")

                # 2. Publish container
                publish_response = client.post(
                    f"{THREADS_API_BASE}/{self.user_id}/threads_publish",
                    data={
                        "creation_id": container_id,
                        "access_token": self.access_token,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if publish_response.status_code != 200:
                    raise RuntimeError(
                        f"Failed to publish thread: {publish_response.text}"
                    )

                thread_id = publish_response.json().get("id")

                return {
                    "thread_id": thread_id,
                    "url": f"https://threads.net/@{self.user_id}/post/{thread_id}",
                }

            # 이미지 포함 게시 (향후 구현)
            else:
                raise NotImplementedError("Image posting not yet implemented")
