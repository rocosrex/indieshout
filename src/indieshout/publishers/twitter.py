import os

import tweepy

from indieshout.formatter.content_formatter import ContentFormatter
from indieshout.models.content import Content
from indieshout.publishers.base import BasePublisher

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGES = 4


class TwitterPublisher(BasePublisher):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.client: tweepy.Client | None = None
        self.api: tweepy.API | None = None
        self._formatter = ContentFormatter()

    def authenticate(self) -> bool:
        twitter_config = self.config.get("twitter", {})
        api_key = twitter_config.get("api_key", "")
        api_secret = twitter_config.get("api_secret", "")
        access_token = twitter_config.get("access_token", "")
        access_token_secret = twitter_config.get("access_token_secret", "")

        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret, access_token, access_token_secret
        )
        self.api = tweepy.API(auth)

        # 인증 검증
        me = self.client.get_me()
        if me.data is None:
            raise tweepy.TweepyException("Authentication failed: could not get user info")

        return True

    def validate(self, content: Content) -> bool:
        if not content.text or not content.text.strip():
            raise ValueError("Text content is required")

        if self.client is None:
            raise RuntimeError("Not authenticated. Call authenticate() first")

        if content.image_paths:
            if len(content.image_paths) > MAX_IMAGES:
                raise ValueError(f"Maximum {MAX_IMAGES} images allowed, got {len(content.image_paths)}")

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
        text = self._formatter._format_x(content)
        return {"text": text}

    def publish(self, content: Content) -> dict:
        formatted = self.format_content(content)
        media_ids = []

        if content.image_paths:
            for path in content.image_paths:
                media = self.api.media_upload(filename=path)
                media_ids.append(media.media_id)

        kwargs: dict = {"text": formatted["text"]}
        if media_ids:
            kwargs["media_ids"] = media_ids

        response = self.client.create_tweet(**kwargs)
        tweet_id = response.data["id"]

        return {
            "tweet_id": tweet_id,
            "url": f"https://x.com/i/status/{tweet_id}",
        }
