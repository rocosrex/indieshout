"""블로그 콘텐츠 폴더에서 Content 객체 로드."""

import re
from datetime import datetime
from pathlib import Path

from indieshout.models.content import Content, ContentType


class ContentLoader:
    """blog-content 폴더 구조에서 Content 객체 생성."""

    def __init__(self, blog_content_dir: str | Path = "blog-content"):
        """ContentLoader 초기화.

        Args:
            blog_content_dir: blog-content 디렉토리 경로
        """
        self.blog_content_dir = Path(blog_content_dir)
        if not self.blog_content_dir.exists():
            self.blog_content_dir.mkdir(parents=True, exist_ok=True)

    def load_from_folder(self, folder_name: str) -> dict:
        """폴더에서 블로그 콘텐츠 로드.

        폴더 구조:
            blog-content/
                {folder_name}/
                    content.md    # 블로그 본문
                    meta.md       # SNS용 텍스트 + 메타데이터
                    assets/       # 이미지들 (1.jpg, 2.png, ...)

        Args:
            folder_name: 블로그 폴더 이름

        Returns:
            dict with keys:
                - blog_content: Content 객체 (블로그용)
                - sns_text: SNS용 텍스트
                - platforms: 게시할 SNS 플랫폼 리스트

        Raises:
            FileNotFoundError: 필수 파일이 없을 때
            ValueError: 파일 형식이 잘못되었을 때
        """
        folder_path = self.blog_content_dir / folder_name

        if not folder_path.exists():
            raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder_path}")

        # content.md 읽기
        content_file = folder_path / "content.md"
        if not content_file.exists():
            raise FileNotFoundError(f"content.md 파일이 없습니다: {content_file}")

        content_text = content_file.read_text(encoding="utf-8")

        # meta.md 읽기 및 파싱
        meta_file = folder_path / "meta.md"
        if not meta_file.exists():
            raise FileNotFoundError(f"meta.md 파일이 없습니다: {meta_file}")

        meta_data = self._parse_meta_file(meta_file)

        # 이미지 파일 수집 (assets 폴더)
        assets_dir = folder_path / "assets"
        image_paths = []
        if assets_dir.exists():
            # 숫자 순서로 정렬 (1.jpg, 2.png, ...)
            image_files = sorted(
                assets_dir.glob("*"),
                key=lambda p: int(re.match(r"(\d+)", p.stem).group(1))
                if re.match(r"(\d+)", p.stem)
                else 999,
            )
            image_paths = [str(f) for f in image_files if f.is_file()]

        # Content 객체 생성 (블로그용)
        blog_content = Content(
            content_type=ContentType.BLOG,
            title=meta_data.get("title", folder_name),
            text=content_text,
            tags=meta_data.get("tags", []),
            categories=meta_data.get("categories", []),
            image_paths=image_paths if image_paths else None,
            date=datetime.now(),
        )

        return {
            "blog_content": blog_content,
            "sns_text": meta_data.get("sns_text", ""),
            "platforms": meta_data.get("platforms", ["x", "threads"]),
        }

    def _parse_meta_file(self, meta_file: Path) -> dict:
        """meta.md 파일 파싱.

        형식:
            title: 블로그 제목
            tags: python, 개발, AI
            categories: 기술
            platforms: x, threads

            ---

            SNS용 텍스트 내용...

        Args:
            meta_file: meta.md 파일 경로

        Returns:
            파싱된 메타데이터 dict
        """
        text = meta_file.read_text(encoding="utf-8")

        # --- 기준으로 메타데이터와 SNS 텍스트 분리
        if "---" in text:
            meta_part, sns_part = text.split("---", 1)
        else:
            meta_part = text
            sns_part = ""

        meta_data = {}

        # 메타데이터 파싱
        for line in meta_part.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "tags":
                    meta_data["tags"] = [t.strip() for t in value.split(",")]
                elif key == "categories":
                    meta_data["categories"] = [c.strip() for c in value.split(",")]
                elif key == "platforms":
                    meta_data["platforms"] = [p.strip() for p in value.split(",")]
                else:
                    meta_data[key] = value

        # SNS 텍스트
        meta_data["sns_text"] = sns_part.strip()

        return meta_data

    def list_folders(self) -> list[str]:
        """blog-content 디렉토리의 모든 폴더 리스트 반환.

        Returns:
            폴더 이름 리스트
        """
        if not self.blog_content_dir.exists():
            return []

        return [
            f.name
            for f in self.blog_content_dir.iterdir()
            if f.is_dir() and not f.name.startswith(".")
        ]
