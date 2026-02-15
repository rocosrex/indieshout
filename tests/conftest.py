import pytest


@pytest.fixture
def sample_config() -> dict:
    return {
        "twitter": {
            "api_key": "test_key",
            "api_secret": "test_secret",
            "access_token": "test_token",
            "access_token_secret": "test_token_secret",
        },
        "threads": {
            "app_id": "test_app_id",
            "app_secret": "test_app_secret",
            "access_token": "test_access_token",
        },
        "hugo": {
            "blog_repo_path": "./blog-site",
            "content_dir": "content/posts",
            "base_url": "https://example.com",
        },
        "defaults": {
            "tags": ["gamedev", "indiedev"],
            "language": "ko",
        },
    }


@pytest.fixture
def sample_markdown(tmp_path):
    md_file = tmp_path / "test-post.md"
    md_file.write_text(
        "---\n"
        "title: 테스트 포스트\n"
        "tags: [python, dev]\n"
        "---\n"
        "\n"
        "본문 내용입니다.\n"
    )
    return md_file
