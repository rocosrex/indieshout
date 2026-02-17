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


class TestFormatX:
    def setup_method(self):
        self.formatter = ContentFormatter()

    def test_short_text_unchanged(self):
        content = Content(content_type=ContentType.SNS, text="Hello world")
        result = self.formatter._format_x(content)
        assert result == "Hello world"

    def test_short_text_with_tags(self):
        content = Content(content_type=ContentType.SNS, text="Hello", tags=["dev", "python"])
        result = self.formatter._format_x(content)
        assert result == "Hello\n\n#dev #python"

    def test_long_text_truncated(self):
        content = Content(content_type=ContentType.SNS, text="a " * 200)
        result = self.formatter._format_x(content)
        assert len(result) <= 280
        assert result.endswith("...")

    def test_exactly_280_chars_no_truncation(self):
        text = "a" * 280
        content = Content(content_type=ContentType.SNS, text=text)
        result = self.formatter._format_x(content)
        assert result == text
        assert len(result) == 280

    def test_281_chars_truncated(self):
        text = "a" * 281
        content = Content(content_type=ContentType.SNS, text=text)
        result = self.formatter._format_x(content)
        assert len(result) <= 280
        assert result.endswith("...")

    def test_word_boundary_truncation(self):
        # 단어 중간이 아닌 단어 경계에서 잘리는지 확인
        words = "hello world testing truncation"
        text = (words + " ") * 20  # 충분히 긴 텍스트
        content = Content(content_type=ContentType.SNS, text=text.strip())
        result = self.formatter._format_x(content)
        assert len(result) <= 280
        assert result.endswith("...")
        # "..." 앞에 잘린 부분이 공백으로 끝나지 않는지 확인
        without_ellipsis = result[:-3]
        assert not without_ellipsis.endswith(" ")

    def test_long_text_with_tags_fits_280(self):
        text = "word " * 100
        content = Content(content_type=ContentType.SNS, text=text.strip(), tags=["dev"])
        result = self.formatter._format_x(content)
        assert len(result) <= 280
        assert "#dev" in result
        assert result.endswith("#dev")


class TestFormatThreads:
    def setup_method(self):
        self.formatter = ContentFormatter()

    def test_short_text_unchanged(self):
        content = Content(content_type=ContentType.SNS, text="Hello world")
        result = self.formatter._format_threads(content)
        assert result == "Hello world"

    def test_short_text_with_tags(self):
        content = Content(content_type=ContentType.SNS, text="Hello", tags=["dev", "python"])
        result = self.formatter._format_threads(content)
        assert result == "Hello\n\n#dev #python"

    def test_long_text_truncated(self):
        content = Content(content_type=ContentType.SNS, text="a " * 300)
        result = self.formatter._format_threads(content)
        assert len(result) <= 500
        assert result.endswith("...")

    def test_exactly_500_chars_no_truncation(self):
        text = "a" * 500
        content = Content(content_type=ContentType.SNS, text=text)
        result = self.formatter._format_threads(content)
        assert result == text
        assert len(result) == 500

    def test_501_chars_truncated(self):
        text = "a" * 501
        content = Content(content_type=ContentType.SNS, text=text)
        result = self.formatter._format_threads(content)
        assert len(result) <= 500
        assert result.endswith("...")

    def test_word_boundary_truncation(self):
        words = "hello world testing truncation"
        text = (words + " ") * 30
        content = Content(content_type=ContentType.SNS, text=text.strip())
        result = self.formatter._format_threads(content)
        assert len(result) <= 500
        assert result.endswith("...")
        without_ellipsis = result[:-3]
        assert not without_ellipsis.endswith(" ")

    def test_long_text_with_tags_fits_500(self):
        text = "word " * 150
        content = Content(content_type=ContentType.SNS, text=text.strip(), tags=["dev"])
        result = self.formatter._format_threads(content)
        assert len(result) <= 500
        assert "#dev" in result
        assert result.endswith("#dev")
