"""AWS S3 이미지 업로드 유틸리티."""

import mimetypes
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError


class S3Uploader:
    """S3에 파일을 업로드하는 클래스."""

    def __init__(self, config: dict[str, Any]):
        """S3Uploader 초기화.

        Args:
            config: S3 설정 (access_key_id, secret_access_key, bucket_name, region)
        """
        s3_config = config.get("s3", {})
        self.bucket_name = s3_config.get("bucket_name")
        self.region = s3_config.get("region", "ap-northeast-2")

        if not self.bucket_name:
            raise ValueError("S3 bucket_name이 설정되지 않았습니다")

        # boto3 S3 클라이언트 생성
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=s3_config.get("access_key_id"),
            aws_secret_access_key=s3_config.get("secret_access_key"),
            region_name=self.region,
        )

    def upload_file(
        self,
        file_path: str | Path,
        s3_key: str | None = None,
        content_type: str | None = None,
    ) -> str:
        """파일을 S3에 업로드하고 URL 반환.

        Args:
            file_path: 업로드할 파일 경로
            s3_key: S3 객체 키 (None이면 파일명 사용)
            content_type: MIME 타입 (None이면 자동 감지)

        Returns:
            업로드된 파일의 공개 URL

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            ClientError: S3 업로드 실패 시
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        # S3 키 생성 (기본값: 파일명)
        if s3_key is None:
            s3_key = file_path.name

        # Content-Type 자동 감지
        if content_type is None:
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = "application/octet-stream"

        # S3 업로드
        try:
            extra_args = {
                "ContentType": content_type,
                # Note: ACL 대신 버킷 정책으로 public read 권한 설정
            }

            self.s3_client.upload_file(
                str(file_path),
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args,
            )

            # 공개 URL 생성
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            return url

        except ClientError as e:
            raise RuntimeError(f"S3 업로드 실패: {e}") from e

    def upload_multiple(
        self,
        file_paths: list[str | Path],
        s3_prefix: str = "",
    ) -> list[str]:
        """여러 파일을 S3에 업로드.

        Args:
            file_paths: 업로드할 파일 경로 리스트
            s3_prefix: S3 키 접두사 (폴더 경로)

        Returns:
            업로드된 파일들의 URL 리스트
        """
        urls = []
        for file_path in file_paths:
            file_path = Path(file_path)
            s3_key = f"{s3_prefix}/{file_path.name}" if s3_prefix else file_path.name
            url = self.upload_file(file_path, s3_key)
            urls.append(url)

        return urls

    def delete_file(self, s3_key: str) -> None:
        """S3에서 파일 삭제.

        Args:
            s3_key: 삭제할 S3 객체 키

        Raises:
            ClientError: S3 삭제 실패 시
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
        except ClientError as e:
            raise RuntimeError(f"S3 삭제 실패: {e}") from e

    def file_exists(self, s3_key: str) -> bool:
        """S3에 파일이 존재하는지 확인.

        Args:
            s3_key: 확인할 S3 객체 키

        Returns:
            파일 존재 여부
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False
