from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from indieshout.blog.hugo_publisher import HugoPublisher
from indieshout.models.content import Content, ContentType


@pytest.fixture
def hugo_config():
    return {
        "hugo": {
            "blog_repo_path": "/tmp/test-blog-site",
            "content_dir": "content/posts",
            "base_url": "https://example.com",
            "default_language": "ko",
            "languages": ["ko", "en"],
        }
    }


@pytest.fixture
def publisher(hugo_config):
    return HugoPublisher(hugo_config)


class TestInit:
    def test_stores_config(self, publisher, hugo_config):
        assert publisher.config == hugo_config
        assert publisher.blog_repo_path == Path("/tmp/test-blog-site")
        assert publisher.content_dir == "content/posts"
        assert publisher.base_url == "https://example.com"
        assert publisher.default_language == "ko"


class TestAuthenticate:
    @patch("subprocess.run")
    def test_git_config_exists(self, mock_run, publisher):
        mock_run.return_value = MagicMock(returncode=0)
        assert publisher.authenticate() is True

    @patch("subprocess.run")
    def test_git_config_missing_raises(self, mock_run, publisher):
        mock_run.side_effect = Exception("Git not configured")
        with pytest.raises(Exception):
            publisher.authenticate()


class TestValidate:
    def test_empty_text_raises(self, publisher):
        content = Content(content_type=ContentType.BLOG, text="", title="Test")
        with pytest.raises(ValueError, match="Text content is required"):
            publisher.validate(content)

    def test_missing_title_raises(self, publisher):
        content = Content(content_type=ContentType.BLOG, text="Hello")
        with pytest.raises(ValueError, match="Title is required"):
            publisher.validate(content)

    def test_missing_repo_raises(self, publisher):
        content = Content(content_type=ContentType.BLOG, text="Hello", title="Test")
        with pytest.raises(FileNotFoundError, match="Blog repository not found"):
            publisher.validate(content)


class TestFormatContent:
    def test_generates_front_matter(self, publisher):
        content = Content(
            content_type=ContentType.BLOG,
            text="Hello world",
            title="Test Post",
            tags=["test", "hugo"],
            categories=["tech"],
            date=datetime(2026, 2, 17, 12, 0, 0),
        )
        result = publisher.format_content(content)

        assert "title: \"Test Post\"" in result["markdown"]
        assert "date: 2026-02-17T12:00:00+09:00" in result["markdown"]
        assert "tags: ['test', 'hugo']" in result["markdown"]
        assert "categories: ['tech']" in result["markdown"]
        assert "Hello world" in result["markdown"]
        assert "slug" in result

    def test_generates_slug_from_title(self, publisher):
        content = Content(
            content_type=ContentType.BLOG,
            text="Content",
            title="Hello World Test",
        )
        result = publisher.format_content(content)

        assert result["slug"].endswith("-hello-world-test")
        assert result["slug"].startswith("20")  # 날짜 prefix


class TestGetPostUrl:
    def test_returns_correct_url(self, publisher):
        content = Content(
            content_type=ContentType.BLOG,
            text="Hello",
            title="Test",
            slug="test-post",
        )
        url = publisher.get_post_url(content)
        assert url == "https://example.com/ko/posts/test-post/"


class TestGenerateSlug:
    def test_slug_from_english_title(self, publisher):
        slug = publisher._generate_slug("Hello World")
        assert "hello-world" in slug

    def test_slug_from_korean_title(self, publisher):
        slug = publisher._generate_slug("안녕하세요")
        assert len(slug) > 0

    def test_slug_removes_special_chars(self, publisher):
        slug = publisher._generate_slug("Test!@# Post$%^")
        assert "!" not in slug
        assert "@" not in slug
        assert "test" in slug.lower()
        assert "post" in slug.lower()
