import os
import subprocess
from datetime import datetime
from pathlib import Path

from indieshout.blog.base import BaseBlogPublisher
from indieshout.models.content import Content
from indieshout.utils.s3_uploader import S3Uploader
from indieshout.utils.translator import Translator


class HugoPublisher(BaseBlogPublisher):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.hugo_config = config.get("hugo", {})
        self.blog_repo_path = Path(self.hugo_config.get("blog_repo_path", "./blog-site"))
        self.content_dir = self.hugo_config.get("content_dir", "content/posts")
        self.base_url = self.hugo_config.get("base_url", "https://myrestaurant.com")
        self.default_language = self.hugo_config.get("default_language", "ko")
        self.languages = self.hugo_config.get("languages", ["ko", "en"])
        self.translator = Translator(source_lang="ko", target_lang="en")

        # S3 업로더 초기화 (S3 설정이 있을 때만)
        self.s3_uploader = None
        if config.get("s3", {}).get("bucket_name"):
            try:
                self.s3_uploader = S3Uploader(config)
            except Exception as e:
                print(f"Warning: S3Uploader initialization failed: {e}")
                # S3 없이도 작동하도록 계속 진행

    def authenticate(self) -> bool:
        """Hugo는 인증이 필요 없음. Git 설정만 확인."""
        # Git 설정 확인
        try:
            subprocess.run(
                ["git", "config", "user.name"],
                cwd=self.blog_repo_path,
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            raise RuntimeError("Git user.name is not configured")

    def validate(self, content: Content) -> bool:
        """게시 전 유효성 검사."""
        if not content.text or not content.text.strip():
            raise ValueError("Text content is required")

        if not content.title:
            raise ValueError("Title is required")

        # blog_repo_path 존재 확인
        if not self.blog_repo_path.exists():
            raise FileNotFoundError(f"Blog repository not found: {self.blog_repo_path}")

        return True

    def format_content(self, content: Content) -> dict:
        """Hugo front matter + 마크다운 생성."""
        # Front matter 생성
        date = content.date or datetime.now()
        date_str = date.strftime("%Y-%m-%dT%H:%M:%S+09:00")

        front_matter = f"""---
title: "{content.title}"
date: {date_str}
draft: false
tags: {content.tags or []}
categories: {content.categories or []}
---

"""
        markdown = front_matter + content.text

        return {
            "markdown": markdown,
            "slug": content.slug or self._generate_slug(content.title),
        }

    def publish(self, content: Content) -> dict:
        """마크다운 파일 생성, 이미지 S3 업로드, 번역, Git commit/push."""
        formatted = self.format_content(content)
        slug = formatted["slug"]
        markdown = formatted["markdown"]

        # 이미지 S3 업로드 (있을 경우)
        image_url_map = {}
        if content.image_paths and self.s3_uploader:
            image_url_map = self._upload_images_to_s3(content.image_paths, slug)
            # 마크다운의 이미지 경로를 S3 URL로 치환
            markdown = self._replace_image_paths(markdown, image_url_map)

        # 포스트 디렉토리 생성
        post_dir = self.blog_repo_path / self.content_dir / slug
        post_dir.mkdir(parents=True, exist_ok=True)

        # 1. 한글 마크다운 파일 생성
        ko_file = post_dir / "index.ko.md"
        ko_file.write_text(markdown, encoding="utf-8")

        # 2. 영문 번역 파일 생성
        en_file = post_dir / "index.en.md"
        if "en" in self.languages:
            try:
                translated_markdown = self.translator.translate_markdown(markdown)
                en_file.write_text(translated_markdown, encoding="utf-8")
            except Exception as e:
                # 번역 실패 시 경고만 출력하고 계속 진행
                print(f"Warning: Translation failed: {e}")
                # 영문 파일은 생성하지 않음

        # Git commit
        self._git_commit(slug, content.title)

        # URL 생성
        url = self.get_post_url(content)

        return {
            "slug": slug,
            "url": url,
            "files": {
                "ko": str(ko_file),
                "en": str(en_file) if en_file.exists() else None,
            },
            "images": image_url_map,
        }

    def read_post(self, file_path: Path) -> Content:
        """마크다운 파일을 읽어 Content 객체로 변환."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        text = file_path.read_text(encoding="utf-8")

        # Front matter 파싱 (간단 구현)
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                # front_matter = parts[1]
                body = parts[2].strip()
            else:
                body = text
        else:
            body = text

        return Content(
            content_type="blog",
            text=body,
            title=file_path.stem,  # 파일명을 제목으로 사용
        )

    def deploy(self, content: Content) -> bool:
        """Git push로 배포."""
        try:
            subprocess.run(
                ["git", "push"],
                cwd=self.blog_repo_path,
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git push failed: {e.stderr.decode()}")

    def get_post_url(self, content: Content) -> str:
        """게시된 포스트의 URL 반환."""
        slug = content.slug or self._generate_slug(content.title)
        return f"{self.base_url}/{self.default_language}/posts/{slug}/"

    def _generate_slug(self, title: str) -> str:
        """제목에서 slug 생성 (간단 구현)."""
        import re
        import unicodedata

        # 유니코드 정규화
        slug = unicodedata.normalize("NFKD", title)
        # 소문자 변환
        slug = slug.lower()
        # 특수문자 제거, 공백을 하이픈으로
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        slug = slug.strip("-")

        # 날짜 추가 (중복 방지)
        date_prefix = datetime.now().strftime("%Y%m%d")
        return f"{date_prefix}-{slug}"

    def _upload_images_to_s3(self, image_paths: list[str], slug: str) -> dict[str, str]:
        """이미지들을 S3에 업로드하고 로컬 경로 → S3 URL 매핑 반환.

        Args:
            image_paths: 업로드할 이미지 경로 리스트
            slug: 포스트 slug (S3 폴더 이름으로 사용)

        Returns:
            로컬 경로 → S3 URL 매핑 dict
        """
        if not self.s3_uploader:
            return {}

        url_map = {}
        s3_prefix = f"posts/{slug}"

        for image_path in image_paths:
            try:
                path = Path(image_path)
                if not path.exists():
                    print(f"Warning: Image not found: {image_path}")
                    continue

                # S3 업로드
                s3_key = f"{s3_prefix}/{path.name}"
                url = self.s3_uploader.upload_file(path, s3_key)
                url_map[image_path] = url
                print(f"✅ Image uploaded: {path.name} → {url}")

            except Exception as e:
                print(f"Warning: Failed to upload {image_path}: {e}")

        return url_map

    def _replace_image_paths(self, markdown: str, url_map: dict[str, str]) -> str:
        """마크다운의 이미지 경로를 S3 URL로 치환.

        Args:
            markdown: 원본 마크다운 텍스트
            url_map: 로컬 경로 → S3 URL 매핑

        Returns:
            이미지 경로가 치환된 마크다운
        """
        result = markdown
        for local_path, s3_url in url_map.items():
            # 마크다운 이미지 구문: ![alt](path)
            result = result.replace(f"]({local_path})", f"]({s3_url})")
            # HTML img 태그: <img src="path">
            result = result.replace(f'src="{local_path}"', f'src="{s3_url}"')
            result = result.replace(f"src='{local_path}'", f"src='{s3_url}'")

        return result

    def _git_commit(self, slug: str, title: str) -> None:
        """Git add 및 commit."""
        try:
            # Git add
            subprocess.run(
                ["git", "add", self.content_dir],
                cwd=self.blog_repo_path,
                check=True,
                capture_output=True,
            )

            # Git commit
            commit_message = f"Add post: {title}"
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.blog_repo_path,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            # 변경사항이 없으면 에러가 발생할 수 있음 (무시)
            if "nothing to commit" not in e.stderr.decode():
                raise RuntimeError(f"Git commit failed: {e.stderr.decode()}")
