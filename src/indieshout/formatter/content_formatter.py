from indieshout.models.content import Content


class ContentFormatter:
    def format_for_platform(self, content: Content, platform: str) -> str:
        """플랫폼별 포맷 메서드로 동적 디스패치."""
        method_name = f"_format_{platform}"
        formatter = getattr(self, method_name, self._format_default)
        return formatter(content)

    def _format_default(self, content: Content) -> str:
        """기본 포맷터: 본문 + 해시태그."""
        text = content.text

        if content.tags:
            hashtags = " ".join(f"#{tag}" for tag in content.tags)
            text = f"{text}\n\n{hashtags}"

        return text

    def _format_x(self, content: Content) -> str:
        """X (Twitter) 포맷터: 280자 제한, 태그 포함."""
        max_length = 280
        tag_suffix = ""

        if content.tags:
            tag_suffix = "\n\n" + " ".join(f"#{tag}" for tag in content.tags)

        available = max_length - len(tag_suffix)
        text = content.text

        if len(text) > available:
            truncated = text[: available - 3]
            last_space = truncated.rfind(" ")
            if last_space > 0:
                truncated = truncated[:last_space]
            text = truncated + "..."

        return text + tag_suffix

    def _format_threads(self, content: Content) -> str:
        """Threads 포맷터: 500자 제한, 태그 포함."""
        max_length = 500
        tag_suffix = ""

        if content.tags:
            tag_suffix = "\n\n" + " ".join(f"#{tag}" for tag in content.tags)

        available = max_length - len(tag_suffix)
        text = content.text

        if len(text) > available:
            truncated = text[: available - 3]
            last_space = truncated.rfind(" ")
            if last_space > 0:
                truncated = truncated[:last_space]
            text = truncated + "..."

        return text + tag_suffix
