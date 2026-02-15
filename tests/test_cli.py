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
