from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from indieshout.main import cli


class TestCli:
    def setup_method(self):
        self.runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "IndieShout" in result.output

    def test_blog_help(self):
        result = self.runner.invoke(cli, ["blog", "--help"])
        assert result.exit_code == 0
        assert "publish" in result.output

    def test_sns_help(self):
        result = self.runner.invoke(cli, ["sns", "--help"])
        assert result.exit_code == 0
        assert "post" in result.output

    def test_blog_publish_dry_run(self, sample_markdown):
        result = self.runner.invoke(cli, ["blog", "publish", str(sample_markdown)])
        assert result.exit_code == 0
        assert "dry-run" in result.output
        assert "blog" in result.output

    def test_blog_publish_with_platforms(self, sample_markdown):
        result = self.runner.invoke(
            cli, ["blog", "publish", str(sample_markdown), "--platforms", "x,threads"]
        )
        assert result.exit_code == 0
        assert "x" in result.output
        assert "threads" in result.output

    def test_sns_post_dry_run(self):
        result = self.runner.invoke(cli, ["sns", "post", "테스트 게시물"])
        assert result.exit_code == 0
        assert "dry-run" in result.output
        assert "sns" in result.output

    def test_sns_post_with_platforms(self):
        result = self.runner.invoke(
            cli, ["sns", "post", "테스트", "--platforms", "x,threads"]
        )
        assert result.exit_code == 0
        assert "x" in result.output

    def test_blog_publish_missing_file(self):
        result = self.runner.invoke(cli, ["blog", "publish", "nonexistent.md"])
        assert result.exit_code != 0

    def test_sns_post_no_dry_run(self):
        mock_publisher = MagicMock()
        mock_publisher.authenticate.return_value = True
        mock_publisher.validate.return_value = True
        mock_publisher.publish.return_value = {"tweet_id": "123", "url": "https://x.com/i/status/123"}
        mock_cls = MagicMock(return_value=mock_publisher)

        with patch.dict("indieshout.main.PLATFORM_PUBLISHERS", {"x": mock_cls}):
            result = self.runner.invoke(
                cli, ["sns", "post", "Hello!", "--platforms", "x", "--no-dry-run"]
            )
        assert result.exit_code == 0
        assert "게시 완료" in result.output
        mock_publisher.authenticate.assert_called_once()
        mock_publisher.validate.assert_called_once()
        mock_publisher.publish.assert_called_once()
