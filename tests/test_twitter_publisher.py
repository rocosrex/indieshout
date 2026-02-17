import os
from unittest.mock import MagicMock, patch

import pytest
import tweepy

from indieshout.models.content import Content, ContentType
from indieshout.publishers.twitter import (
    MAX_IMAGE_SIZE,
    MAX_IMAGES,
    TwitterPublisher,
)


@pytest.fixture
def twitter_config():
    return {
        "twitter": {
            "api_key": "test_key",
            "api_secret": "test_secret",
            "access_token": "test_token",
            "access_token_secret": "test_token_secret",
        }
    }


@pytest.fixture
def publisher(twitter_config):
    return TwitterPublisher(twitter_config)


@pytest.fixture
def authenticated_publisher(publisher):
    """authenticate() 호출 없이 client/api가 설정된 publisher."""
    publisher.client = MagicMock(spec=tweepy.Client)
    publisher.api = MagicMock(spec=tweepy.API)
    return publisher


class TestInit:
    def test_stores_config(self, publisher, twitter_config):
        assert publisher.config == twitter_config

    def test_client_none_before_auth(self, publisher):
        assert publisher.client is None

    def test_api_none_before_auth(self, publisher):
        assert publisher.api is None


class TestAuthenticate:
    @patch("indieshout.publishers.twitter.tweepy.API")
    @patch("indieshout.publishers.twitter.tweepy.OAuth1UserHandler")
    @patch("indieshout.publishers.twitter.tweepy.Client")
    def test_authenticate_success(self, mock_client_cls, mock_auth_cls, mock_api_cls, publisher):
        mock_client = MagicMock()
        mock_client.get_me.return_value = MagicMock(data={"id": "123", "name": "test"})
        mock_client_cls.return_value = mock_client

        result = publisher.authenticate()

        assert result is True
        assert publisher.client is mock_client
        mock_client.get_me.assert_called_once()

    @patch("indieshout.publishers.twitter.tweepy.API")
    @patch("indieshout.publishers.twitter.tweepy.OAuth1UserHandler")
    @patch("indieshout.publishers.twitter.tweepy.Client")
    def test_authenticate_failure_no_user(self, mock_client_cls, mock_auth_cls, mock_api_cls, publisher):
        mock_client = MagicMock()
        mock_client.get_me.return_value = MagicMock(data=None)
        mock_client_cls.return_value = mock_client

        with pytest.raises(tweepy.TweepyException, match="Authentication failed"):
            publisher.authenticate()

    @patch("indieshout.publishers.twitter.tweepy.API")
    @patch("indieshout.publishers.twitter.tweepy.OAuth1UserHandler")
    @patch("indieshout.publishers.twitter.tweepy.Client")
    def test_authenticate_api_error(self, mock_client_cls, mock_auth_cls, mock_api_cls, publisher):
        mock_client = MagicMock()
        mock_client.get_me.side_effect = tweepy.TweepyException("API error")
        mock_client_cls.return_value = mock_client

        with pytest.raises(tweepy.TweepyException, match="API error"):
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
        paths = []
        for i in range(MAX_IMAGES + 1):
            p = tmp_path / f"img{i}.jpg"
            p.write_bytes(b"\xff\xd8" + b"\x00" * 100)
            paths.append(str(p))

        content = Content(content_type=ContentType.SNS, text="hello", image_paths=paths)
        with pytest.raises(ValueError, match="Maximum 4 images"):
            authenticated_publisher.validate(content)

    def test_image_not_found_raises(self, authenticated_publisher):
        content = Content(
            content_type=ContentType.SNS, text="hello", image_paths=["/nonexistent/img.jpg"]
        )
        with pytest.raises(FileNotFoundError, match="Image not found"):
            authenticated_publisher.validate(content)

    def test_unsupported_image_format_raises(self, authenticated_publisher, tmp_path):
        bmp = tmp_path / "test.bmp"
        bmp.write_bytes(b"\x00" * 100)
        content = Content(content_type=ContentType.SNS, text="hello", image_paths=[str(bmp)])
        with pytest.raises(ValueError, match="Unsupported image format"):
            authenticated_publisher.validate(content)

    def test_image_too_large_raises(self, authenticated_publisher, tmp_path):
        large = tmp_path / "big.jpg"
        large.write_bytes(b"\x00" * (MAX_IMAGE_SIZE + 1))
        content = Content(content_type=ContentType.SNS, text="hello", image_paths=[str(large)])
        with pytest.raises(ValueError, match="Image too large"):
            authenticated_publisher.validate(content)

    def test_valid_content_passes(self, authenticated_publisher):
        content = Content(content_type=ContentType.SNS, text="hello world")
        assert authenticated_publisher.validate(content) is True

    def test_valid_content_with_images(self, authenticated_publisher, tmp_path):
        img = tmp_path / "photo.jpg"
        img.write_bytes(b"\xff\xd8" + b"\x00" * 100)
        content = Content(content_type=ContentType.SNS, text="hello", image_paths=[str(img)])
        assert authenticated_publisher.validate(content) is True


class TestFormatContent:
    def test_delegates_to_formatter(self, authenticated_publisher):
        content = Content(content_type=ContentType.SNS, text="Hello world", tags=["dev"])
        result = authenticated_publisher.format_content(content)
        assert result == {"text": "Hello world\n\n#dev"}


class TestPublish:
    def test_text_only(self, authenticated_publisher):
        content = Content(content_type=ContentType.SNS, text="Hello!")
        authenticated_publisher.client.create_tweet.return_value = MagicMock(
            data={"id": "12345"}
        )

        result = authenticated_publisher.publish(content)

        authenticated_publisher.client.create_tweet.assert_called_once_with(text="Hello!")
        assert result["tweet_id"] == "12345"
        assert "12345" in result["url"]

    def test_with_image(self, authenticated_publisher, tmp_path):
        img = tmp_path / "photo.jpg"
        img.write_bytes(b"\xff\xd8" + b"\x00" * 100)

        content = Content(content_type=ContentType.SNS, text="With image", image_paths=[str(img)])

        mock_media = MagicMock()
        mock_media.media_id = 999
        authenticated_publisher.api.media_upload.return_value = mock_media
        authenticated_publisher.client.create_tweet.return_value = MagicMock(
            data={"id": "67890"}
        )

        result = authenticated_publisher.publish(content)

        authenticated_publisher.api.media_upload.assert_called_once_with(filename=str(img))
        authenticated_publisher.client.create_tweet.assert_called_once_with(
            text="With image", media_ids=[999]
        )
        assert result["tweet_id"] == "67890"

    def test_with_multiple_images(self, authenticated_publisher, tmp_path):
        paths = []
        for i in range(3):
            p = tmp_path / f"img{i}.png"
            p.write_bytes(b"\x89PNG" + b"\x00" * 100)
            paths.append(str(p))

        content = Content(content_type=ContentType.SNS, text="Multi", image_paths=paths)

        media_mocks = []
        for i in range(3):
            m = MagicMock()
            m.media_id = 100 + i
            media_mocks.append(m)
        authenticated_publisher.api.media_upload.side_effect = media_mocks
        authenticated_publisher.client.create_tweet.return_value = MagicMock(
            data={"id": "11111"}
        )

        result = authenticated_publisher.publish(content)

        assert authenticated_publisher.api.media_upload.call_count == 3
        authenticated_publisher.client.create_tweet.assert_called_once_with(
            text="Multi", media_ids=[100, 101, 102]
        )
        assert result["tweet_id"] == "11111"
