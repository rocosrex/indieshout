import os
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from indieshout.models.content import Content, ContentType
from indieshout.publishers.threads import (
    MAX_IMAGE_SIZE,
    MAX_IMAGES,
    ThreadsPublisher,
)


@pytest.fixture
def threads_config():
    return {
        "threads": {
            "access_token": "test_access_token",
            "user_id": "test_user_id",
        }
    }


@pytest.fixture
def publisher(threads_config):
    return ThreadsPublisher(threads_config)


@pytest.fixture
def authenticated_publisher(publisher):
    """authenticate() 호출 없이 access_token/user_id가 설정된 publisher."""
    publisher.access_token = "test_access_token"
    publisher.user_id = "test_user_id"
    return publisher


class TestInit:
    def test_stores_config(self, publisher, threads_config):
        assert publisher.config == threads_config

    def test_access_token_none_before_auth(self, publisher):
        assert publisher.access_token is None

    def test_user_id_none_before_auth(self, publisher):
        assert publisher.user_id is None


class TestAuthenticate:
    @patch("indieshout.publishers.threads.httpx.Client")
    def test_authenticate_success(self, mock_client_cls, publisher):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_user_id", "username": "testuser"}

        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = publisher.authenticate()

        assert result is True
        assert publisher.access_token == "test_access_token"
        assert publisher.user_id == "test_user_id"

    @patch("indieshout.publishers.threads.httpx.Client")
    def test_authenticate_failure_invalid_token(self, mock_client_cls, publisher):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid token"

        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="Authentication failed"):
            publisher.authenticate()

    def test_authenticate_missing_credentials(self):
        publisher = ThreadsPublisher({"threads": {}})
        with pytest.raises(ValueError, match="access_token and user_id are required"):
            publisher.authenticate()


class TestValidate:
    def test_empty_text_raises(self, authenticated_publisher):
        content = Content(content_type=ContentType.SNS, text="")
        with pytest.raises(ValueError, match="Text content is required"):
            authenticated_publisher.validate(content)

    def test_whitespace_text_raises(self, authenticated_publisher):
        content = Content(content_type=ContentType.SNS, text="   ")
        with pytest.raises(ValueError, match="Text content is required"):
            authenticated_publisher.validate(content)

    def test_not_authenticated_raises(self, publisher):
        content = Content(content_type=ContentType.SNS, text="hello")
        with pytest.raises(RuntimeError, match="Not authenticated"):
            publisher.validate(content)

    def test_too_many_images_raises(self, authenticated_publisher, tmp_path):
        images = [str(tmp_path / f"img{i}.jpg") for i in range(MAX_IMAGES + 1)]
        for img in images:
            with open(img, "wb") as f:
                f.write(b"fake")

        content = Content(content_type=ContentType.SNS, text="test", image_paths=images)
        with pytest.raises(ValueError, match=f"Maximum {MAX_IMAGES} images"):
            authenticated_publisher.validate(content)

    def test_image_not_found_raises(self, authenticated_publisher):
        content = Content(
            content_type=ContentType.SNS, text="test", image_paths=["/fake/path.jpg"]
        )
        with pytest.raises(FileNotFoundError, match="Image not found"):
            authenticated_publisher.validate(content)

    def test_unsupported_image_format_raises(self, authenticated_publisher, tmp_path):
        bad_img = tmp_path / "test.bmp"
        bad_img.write_bytes(b"fake")

        content = Content(
            content_type=ContentType.SNS, text="test", image_paths=[str(bad_img)]
        )
        with pytest.raises(ValueError, match="Unsupported image format"):
            authenticated_publisher.validate(content)

    def test_image_too_large_raises(self, authenticated_publisher, tmp_path):
        large_img = tmp_path / "large.jpg"
        large_img.write_bytes(b"x" * (MAX_IMAGE_SIZE + 1))

        content = Content(
            content_type=ContentType.SNS, text="test", image_paths=[str(large_img)]
        )
        with pytest.raises(ValueError, match="Image too large"):
            authenticated_publisher.validate(content)

    def test_valid_content_passes(self, authenticated_publisher):
        content = Content(content_type=ContentType.SNS, text="Valid text")
        assert authenticated_publisher.validate(content) is True

    def test_valid_content_with_images(self, authenticated_publisher, tmp_path):
        img = tmp_path / "test.jpg"
        img.write_bytes(b"fake image" * 100)

        content = Content(
            content_type=ContentType.SNS, text="test", image_paths=[str(img)]
        )
        assert authenticated_publisher.validate(content) is True


class TestFormatContent:
    def test_delegates_to_formatter(self, authenticated_publisher):
        content = Content(content_type=ContentType.SNS, text="Hello", tags=["test"])
        result = authenticated_publisher.format_content(content)

        assert "text" in result
        assert "Hello" in result["text"]
        assert "#test" in result["text"]


class TestPublish:
    @patch("indieshout.publishers.threads.httpx.Client")
    def test_text_only(self, mock_client_cls, authenticated_publisher):
        mock_create_response = Mock()
        mock_create_response.status_code = 200
        mock_create_response.json.return_value = {"id": "container_123"}

        mock_publish_response = Mock()
        mock_publish_response.status_code = 200
        mock_publish_response.json.return_value = {"id": "thread_456"}

        mock_client = MagicMock()
        mock_client.__enter__.return_value.post.side_effect = [
            mock_create_response,
            mock_publish_response,
        ]
        mock_client_cls.return_value = mock_client

        content = Content(content_type=ContentType.SNS, text="Test post")
        result = authenticated_publisher.publish(content)

        assert result["thread_id"] == "thread_456"
        assert "url" in result

    @patch("indieshout.publishers.threads.httpx.Client")
    def test_with_image_not_implemented(self, mock_client_cls, authenticated_publisher, tmp_path):
        img = tmp_path / "test.jpg"
        img.write_bytes(b"fake")

        content = Content(
            content_type=ContentType.SNS, text="Test", image_paths=[str(img)]
        )

        with pytest.raises(NotImplementedError, match="Image posting not yet implemented"):
            authenticated_publisher.publish(content)
