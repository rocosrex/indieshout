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


class TestS3Integration:
    """S3 이미지 업로드 통합 테스트."""

    @pytest.fixture
    def config_with_s3(self, hugo_config):
        """S3 설정이 포함된 config."""
        hugo_config["s3"] = {
            "access_key_id": "test_key",
            "secret_access_key": "test_secret",
            "bucket_name": "test-bucket",
            "region": "ap-northeast-2",
        }
        return hugo_config

    @patch("boto3.client")
    def test_s3_uploader_initialized_with_s3_config(self, mock_boto, config_with_s3):
        """S3 설정이 있으면 S3Uploader 초기화."""
        publisher = HugoPublisher(config_with_s3)
        assert publisher.s3_uploader is not None
        assert publisher.s3_uploader.bucket_name == "test-bucket"

    def test_s3_uploader_none_without_s3_config(self, hugo_config):
        """S3 설정이 없으면 S3Uploader는 None."""
        publisher = HugoPublisher(hugo_config)
        assert publisher.s3_uploader is None

    @patch("boto3.client")
    def test_upload_images_to_s3(self, mock_boto, config_with_s3, tmp_path):
        """이미지를 S3에 업로드."""
        publisher = HugoPublisher(config_with_s3)

        # 테스트 이미지 생성
        image1 = tmp_path / "image1.jpg"
        image2 = tmp_path / "image2.png"
        image1.write_text("fake image 1")
        image2.write_text("fake image 2")

        # S3 업로드 모킹
        publisher.s3_uploader.s3_client.upload_file = MagicMock()

        # 업로드 실행
        url_map = publisher._upload_images_to_s3(
            [str(image1), str(image2)], "test-slug"
        )

        # 검증
        assert len(url_map) == 2
        assert str(image1) in url_map
        assert str(image2) in url_map
        assert "test-slug" in url_map[str(image1)]
        assert "image1.jpg" in url_map[str(image1)]

    def test_replace_image_paths(self, publisher):
        """마크다운의 이미지 경로를 S3 URL로 치환."""
        markdown = """
# 제목

![Image 1](/path/to/image1.jpg)

Some text here.

![Image 2](/path/to/image2.png)
"""
        url_map = {
            "/path/to/image1.jpg": "https://s3.amazonaws.com/bucket/image1.jpg",
            "/path/to/image2.png": "https://s3.amazonaws.com/bucket/image2.png",
        }

        result = publisher._replace_image_paths(markdown, url_map)

        assert "/path/to/image1.jpg" not in result
        assert "/path/to/image2.png" not in result
        assert "https://s3.amazonaws.com/bucket/image1.jpg" in result
        assert "https://s3.amazonaws.com/bucket/image2.png" in result

    def test_replace_image_paths_html(self, publisher):
        """HTML img 태그의 경로도 치환."""
        markdown = '<img src="/local/image.jpg" alt="test">'
        url_map = {"/local/image.jpg": "https://s3.amazonaws.com/image.jpg"}

        result = publisher._replace_image_paths(markdown, url_map)

        assert "/local/image.jpg" not in result
        assert "https://s3.amazonaws.com/image.jpg" in result
