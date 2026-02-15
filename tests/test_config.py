import os

from indieshout.utils.config import load_config, _inject_env_secrets


class TestLoadConfig:
    def test_load_from_yaml(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(
            "twitter:\n"
            "  api_key: yaml_key\n"
            "defaults:\n"
            "  language: ko\n"
        )
        config = load_config(str(yaml_file))
        assert config["twitter"]["api_key"] == "yaml_key"
        assert config["defaults"]["language"] == "ko"

    def test_missing_yaml_returns_empty(self, tmp_path):
        config = load_config(str(tmp_path / "nonexistent.yaml"))
        assert isinstance(config, dict)

    def test_env_overrides_yaml(self, tmp_path, monkeypatch):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(
            "twitter:\n"
            "  api_key: yaml_key\n"
        )
        monkeypatch.setenv("TWITTER_API_KEY", "env_key")
        config = load_config(str(yaml_file))
        assert config["twitter"]["api_key"] == "env_key"

    def test_env_creates_section_if_missing(self, tmp_path, monkeypatch):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("defaults:\n  language: ko\n")
        monkeypatch.setenv("TWITTER_API_KEY", "env_key")
        config = load_config(str(yaml_file))
        assert config["twitter"]["api_key"] == "env_key"


class TestInjectEnvSecrets:
    def test_inject_multiple_vars(self, monkeypatch):
        monkeypatch.setenv("TWITTER_API_KEY", "tk")
        monkeypatch.setenv("THREADS_APP_ID", "tid")
        config = _inject_env_secrets({})
        assert config["twitter"]["api_key"] == "tk"
        assert config["threads"]["app_id"] == "tid"

    def test_no_env_vars_no_change(self):
        config = {"twitter": {"api_key": "original"}}
        result = _inject_env_secrets(config)
        assert result["twitter"]["api_key"] == "original"
