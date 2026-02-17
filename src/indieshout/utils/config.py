import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# 환경변수 → config dict 키 매핑
_ENV_MAPPING: dict[str, tuple[str, str]] = {
    "TWITTER_API_KEY": ("twitter", "api_key"),
    "TWITTER_API_SECRET": ("twitter", "api_secret"),
    "TWITTER_ACCESS_TOKEN": ("twitter", "access_token"),
    "TWITTER_ACCESS_TOKEN_SECRET": ("twitter", "access_token_secret"),
    "THREADS_APP_ID": ("threads", "app_id"),
    "THREADS_APP_SECRET": ("threads", "app_secret"),
    "THREADS_ACCESS_TOKEN": ("threads", "access_token"),
    "THREADS_USER_ID": ("threads", "user_id"),
    "YOUTUBE_CLIENT_ID": ("youtube", "client_id"),
    "YOUTUBE_CLIENT_SECRET": ("youtube", "client_secret"),
    "AWS_S3_BUCKET": ("s3", "bucket_name"),
    "AWS_S3_REGION": ("s3", "region"),
}


def _inject_env_secrets(config: dict) -> dict:
    """환경변수 값으로 config dict를 오버라이드."""
    for env_var, (section, key) in _ENV_MAPPING.items():
        value = os.environ.get(env_var)
        if value:
            config.setdefault(section, {})[key] = value
    return config


def load_config(config_path: str | None = None) -> dict:
    """config.yaml + .env 병합하여 설정 로드.

    .env 값이 yaml 값을 오버라이드한다.
    """
    load_dotenv()

    config: dict = {}

    if config_path is None:
        config_path = "config/config.yaml"

    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            config = yaml.safe_load(f) or {}

    config = _inject_env_secrets(config)

    return config
