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
