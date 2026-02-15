from indieshout.formatter.content_formatter import ContentFormatter
from indieshout.models.content import Content, ContentType


class TestContentFormatter:
    def setup_method(self):
        self.formatter = ContentFormatter()

    def test_format_default_no_tags(self):
        content = Content(content_type=ContentType.SNS, text="Hello world")
        result = self.formatter.format_for_platform(content, "default")
        assert result == "Hello world"

    def test_format_default_with_tags(self):
        content = Content(
            content_type=ContentType.SNS,
            text="Hello world",
            tags=["python", "dev"],
        )
        result = self.formatter.format_for_platform(content, "default")
        assert result == "Hello world\n\n#python #dev"

    def test_format_unknown_platform_uses_default(self):
        content = Content(content_type=ContentType.SNS, text="test")
        result = self.formatter.format_for_platform(content, "unknown_platform")
        assert result == "test"

    def test_format_dispatches_to_platform_method(self):
        def _format_custom(content: Content) -> str:
            return f"[CUSTOM] {content.text}"

        self.formatter._format_custom = _format_custom
        content = Content(content_type=ContentType.SNS, text="hello")
        result = self.formatter.format_for_platform(content, "custom")
        assert result == "[CUSTOM] hello"
