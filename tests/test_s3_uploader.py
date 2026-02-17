"""S3Uploader 테스트."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from indieshout.utils.s3_uploader import S3Uploader


@pytest.fixture
def mock_config():
    """테스트용 설정."""
    return {
        "s3": {
            "access_key_id": "test_key",
            "secret_access_key": "test_secret",
            "bucket_name": "test-bucket",
            "region": "ap-northeast-2",
        }
    }


@pytest.fixture
def uploader(mock_config):
    """S3Uploader 인스턴스."""
    with patch("boto3.client"):
        return S3Uploader(mock_config)


def test_init_without_bucket_name():
    """버킷 이름 없이 초기화 시 에러."""
    config = {"s3": {}}
    with pytest.raises(ValueError, match="bucket_name"):
        S3Uploader(config)


def test_init_with_config(mock_config):
    """설정으로 초기화."""
    with patch("boto3.client") as mock_client:
        uploader = S3Uploader(mock_config)
        assert uploader.bucket_name == "test-bucket"
        assert uploader.region == "ap-northeast-2"
        mock_client.assert_called_once()


def test_upload_file_not_found(uploader):
    """존재하지 않는 파일 업로드 시 에러."""
    with pytest.raises(FileNotFoundError):
        uploader.upload_file("/nonexistent/file.txt")


def test_upload_file_success(uploader):
    """파일 업로드 성공."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"test content")
        temp_file = Path(f.name)

    try:
        # S3 클라이언트 모킹
        uploader.s3_client.upload_file = MagicMock()

        url = uploader.upload_file(temp_file, "test/file.txt")

        assert url == "https://test-bucket.s3.ap-northeast-2.amazonaws.com/test/file.txt"
        uploader.s3_client.upload_file.assert_called_once()

    finally:
        temp_file.unlink()


def test_upload_file_with_auto_key(uploader):
    """S3 키 자동 생성."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"fake image")
        temp_file = Path(f.name)

    try:
        uploader.s3_client.upload_file = MagicMock()

        url = uploader.upload_file(temp_file)

        # 파일명이 S3 키로 사용됨
        expected_url = (
            f"https://test-bucket.s3.ap-northeast-2.amazonaws.com/{temp_file.name}"
        )
        assert url == expected_url

    finally:
        temp_file.unlink()


def test_upload_multiple(uploader):
    """여러 파일 업로드."""
    files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(suffix=f".txt", delete=False) as f:
            f.write(f"content {i}".encode())
            files.append(Path(f.name))

    try:
        uploader.s3_client.upload_file = MagicMock()

        urls = uploader.upload_multiple(files, "test-prefix")

        assert len(urls) == 3
        for url in urls:
            assert "test-prefix" in url

    finally:
        for f in files:
            f.unlink()


def test_file_exists(uploader):
    """파일 존재 확인."""
    uploader.s3_client.head_object = MagicMock()

    assert uploader.file_exists("test-key") is True

    uploader.s3_client.head_object.assert_called_once_with(
        Bucket="test-bucket", Key="test-key"
    )


def test_file_not_exists(uploader):
    """파일 존재하지 않음."""
    from botocore.exceptions import ClientError

    error_response = {"Error": {"Code": "404"}}
    uploader.s3_client.head_object = MagicMock(
        side_effect=ClientError(error_response, "HeadObject")
    )

    assert uploader.file_exists("nonexistent") is False


def test_delete_file(uploader):
    """파일 삭제."""
    uploader.s3_client.delete_object = MagicMock()

    uploader.delete_file("test-key")

    uploader.s3_client.delete_object.assert_called_once_with(
        Bucket="test-bucket", Key="test-key"
    )
