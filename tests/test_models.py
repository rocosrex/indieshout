from datetime import datetime

import pytest
from pydantic import ValidationError

from indieshout.models.content import Content, ContentType


class TestContentType:
    def test_blog_value(self):
        assert ContentType.BLOG == "blog"

    def test_sns_value(self):
        assert ContentType.SNS == "sns"

    def test_from_string(self):
        assert ContentType("blog") is ContentType.BLOG
        assert ContentType("sns") is ContentType.SNS


class TestContent:
    def test_minimal_content(self):
        content = Content(content_type=ContentType.SNS, text="Hello")
        assert content.content_type == ContentType.SNS
        assert content.text == "Hello"
        assert content.platforms == []
        assert content.title is None
        assert content.image_paths is None
        assert content.tags is None

    def test_full_content(self):
        content = Content(
            content_type=ContentType.BLOG,
            text="본문",
            title="제목",
            image_paths=["/img/a.png", "/img/b.png"],
            video_path="/video/v.mp4",
            tags=["python", "dev"],
            platforms=["x", "threads"],
            sns_text="SNS 요약",
            scheduled_at=datetime(2026, 3, 1, 12, 0, 0),
        )
        assert content.title == "제목"
        assert len(content.image_paths) == 2
        assert content.video_path == "/video/v.mp4"
        assert content.sns_text == "SNS 요약"
        assert content.scheduled_at == datetime(2026, 3, 1, 12, 0, 0)

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            Content(text="no type")

        with pytest.raises(ValidationError):
            Content(content_type=ContentType.SNS)

    def test_invalid_content_type(self):
        with pytest.raises(ValidationError):
            Content(content_type="invalid", text="test")
