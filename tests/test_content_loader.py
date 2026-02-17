"""ContentLoader 테스트."""

import tempfile
from pathlib import Path

import pytest

from indieshout.blog.content_loader import ContentLoader
from indieshout.models.content import ContentType


@pytest.fixture
def temp_blog_dir(tmp_path):
    """임시 blog-content 디렉토리."""
    blog_dir = tmp_path / "blog-content"
    blog_dir.mkdir()
    return blog_dir


@pytest.fixture
def sample_folder(temp_blog_dir):
    """샘플 블로그 폴더."""
    folder = temp_blog_dir / "test-post"
    folder.mkdir()

    # content.md
    content_file = folder / "content.md"
    content_file.write_text("# 테스트\n\n본문 내용입니다.", encoding="utf-8")

    # meta.md
    meta_file = folder / "meta.md"
    meta_file.write_text(
        """title: 테스트 포스트
tags: python, test
categories: 개발
platforms: x, threads

---

SNS용 텍스트입니다!
""",
        encoding="utf-8",
    )

    # assets
    assets_dir = folder / "assets"
    assets_dir.mkdir()
    (assets_dir / "1.jpg").write_text("fake image 1")
    (assets_dir / "2.png").write_text("fake image 2")

    return folder


def test_init_creates_directory(tmp_path):
    """디렉토리 자동 생성."""
    loader = ContentLoader(tmp_path / "new-blog-content")
    assert loader.blog_content_dir.exists()


def test_load_from_folder_success(temp_blog_dir, sample_folder):
    """폴더에서 성공적으로 로드."""
    loader = ContentLoader(temp_blog_dir)
    data = loader.load_from_folder("test-post")

    assert data["blog_content"].content_type == ContentType.BLOG
    assert data["blog_content"].title == "테스트 포스트"
    assert "테스트" in data["blog_content"].text
    assert data["blog_content"].tags == ["python", "test"]
    assert data["blog_content"].categories == ["개발"]
    assert len(data["blog_content"].image_paths) == 2
    assert data["sns_text"] == "SNS용 텍스트입니다!"
    assert data["platforms"] == ["x", "threads"]


def test_load_from_folder_missing_folder(temp_blog_dir):
    """존재하지 않는 폴더."""
    loader = ContentLoader(temp_blog_dir)
    with pytest.raises(FileNotFoundError, match="폴더를 찾을 수 없습니다"):
        loader.load_from_folder("nonexistent")


def test_load_from_folder_missing_content_md(temp_blog_dir):
    """content.md 파일 없음."""
    folder = temp_blog_dir / "incomplete"
    folder.mkdir()
    (folder / "meta.md").write_text("title: test\n---\ntext")

    loader = ContentLoader(temp_blog_dir)
    with pytest.raises(FileNotFoundError, match="content.md"):
        loader.load_from_folder("incomplete")


def test_load_from_folder_missing_meta_md(temp_blog_dir):
    """meta.md 파일 없음."""
    folder = temp_blog_dir / "incomplete"
    folder.mkdir()
    (folder / "content.md").write_text("# test")

    loader = ContentLoader(temp_blog_dir)
    with pytest.raises(FileNotFoundError, match="meta.md"):
        loader.load_from_folder("incomplete")


def test_load_from_folder_no_images(temp_blog_dir):
    """이미지 없는 경우."""
    folder = temp_blog_dir / "no-images"
    folder.mkdir()
    (folder / "content.md").write_text("# test")
    (folder / "meta.md").write_text("title: test\n---\ntext")

    loader = ContentLoader(temp_blog_dir)
    data = loader.load_from_folder("no-images")

    assert data["blog_content"].image_paths is None


def test_parse_meta_file_minimal(temp_blog_dir):
    """최소 메타데이터."""
    folder = temp_blog_dir / "minimal"
    folder.mkdir()
    (folder / "content.md").write_text("# test")
    meta_file = folder / "meta.md"
    meta_file.write_text("title: Minimal\n---\nSNS text")

    loader = ContentLoader(temp_blog_dir)
    data = loader.load_from_folder("minimal")

    assert data["blog_content"].title == "Minimal"
    assert data["sns_text"] == "SNS text"
    assert data["platforms"] == ["x", "threads"]  # 기본값


def test_list_folders(temp_blog_dir):
    """폴더 목록 조회."""
    (temp_blog_dir / "post1").mkdir()
    (temp_blog_dir / "post2").mkdir()
    (temp_blog_dir / ".hidden").mkdir()

    loader = ContentLoader(temp_blog_dir)
    folders = loader.list_folders()

    assert len(folders) == 2
    assert "post1" in folders
    assert "post2" in folders
    assert ".hidden" not in folders


def test_image_sorting_by_number(temp_blog_dir):
    """이미지 번호 순서 정렬."""
    folder = temp_blog_dir / "sorted"
    folder.mkdir()
    (folder / "content.md").write_text("# test")
    (folder / "meta.md").write_text("title: test\n---\ntext")

    assets = folder / "assets"
    assets.mkdir()
    (assets / "10.jpg").write_text("10")
    (assets / "2.jpg").write_text("2")
    (assets / "1.jpg").write_text("1")

    loader = ContentLoader(temp_blog_dir)
    data = loader.load_from_folder("sorted")

    paths = data["blog_content"].image_paths
    assert "1.jpg" in paths[0]
    assert "2.jpg" in paths[1]
    assert "10.jpg" in paths[2]
