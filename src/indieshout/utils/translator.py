import re
import subprocess
from pathlib import Path


class Translator:
    """Claude Code -p 옵션을 사용한 번역기."""

    def __init__(self, source_lang: str = "ko", target_lang: str = "en"):
        self.source_lang = source_lang
        self.target_lang = target_lang

    def translate_markdown(self, markdown: str) -> str:
        """마크다운 전체를 번역 (Front matter 포함)."""
        # Front matter와 본문 분리
        if markdown.startswith("---"):
            parts = markdown.split("---", 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                body = parts[2].strip()

                # Front matter 번역
                translated_front_matter = self._translate_front_matter(front_matter)

                # 본문 번역
                translated_body = self._translate_text(body)

                # 재조합
                return f"---\n{translated_front_matter}\n---\n\n{translated_body}"

        # Front matter 없으면 본문만 번역
        return self._translate_text(markdown)

    def translate_text(self, text: str) -> str:
        """일반 텍스트 번역."""
        return self._translate_text(text)

    def _translate_front_matter(self, front_matter: str) -> str:
        """Front matter 번역 (title, tags, categories)."""
        lines = front_matter.strip().split("\n")
        translated_lines = []

        for line in lines:
            # title: "..." 번역
            if line.startswith("title:"):
                match = re.match(r'title:\s*"(.+)"', line)
                if match:
                    title = match.group(1)
                    translated_title = self._translate_text(title)
                    translated_lines.append(f'title: "{translated_title}"')
                else:
                    translated_lines.append(line)

            # tags: [...] 번역
            elif line.startswith("tags:"):
                match = re.match(r"tags:\s*\[(.+)\]", line)
                if match:
                    tags_str = match.group(1)
                    # ['tag1', 'tag2'] 형식 파싱
                    tags = [
                        t.strip().strip("'\"")
                        for t in tags_str.split(",")
                        if t.strip()
                    ]
                    translated_tags = [self._translate_text(tag) for tag in tags]
                    tags_formatted = ", ".join(f"'{tag}'" for tag in translated_tags)
                    translated_lines.append(f"tags: [{tags_formatted}]")
                else:
                    translated_lines.append(line)

            # categories: [...] 번역
            elif line.startswith("categories:"):
                match = re.match(r"categories:\s*\[(.+)\]", line)
                if match:
                    cats_str = match.group(1)
                    cats = [
                        c.strip().strip("'\"")
                        for c in cats_str.split(",")
                        if c.strip()
                    ]
                    translated_cats = [self._translate_text(cat) for cat in cats]
                    cats_formatted = ", ".join(f"'{cat}'" for cat in translated_cats)
                    translated_lines.append(f"categories: [{cats_formatted}]")
                else:
                    translated_lines.append(line)

            # 나머지 (date, draft 등)는 그대로
            else:
                translated_lines.append(line)

        return "\n".join(translated_lines)

    def _translate_text(self, text: str) -> str:
        """Claude Code -p로 텍스트 번역."""
        if not text or not text.strip():
            return text

        # 번역 프롬프트
        prompt = f"""Translate the following {self.source_lang} text to {self.target_lang}.
Preserve markdown formatting, links, and code blocks.
Only return the translated text, no explanations.

Text to translate:
{text}
"""

        try:
            # 중첩 세션 방지를 위해 CLAUDECODE 환경변수 제거
            import os
            env = os.environ.copy()
            env.pop("CLAUDECODE", None)

            # Claude Code -p 실행
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=180,  # 3분으로 증가
                check=True,
                env=env,
            )

            translated = result.stdout.strip()
            return translated

        except subprocess.TimeoutExpired:
            raise RuntimeError("Translation timeout (180s)")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Translation failed: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Translation error: {e}")

    def translate_file(self, input_file: Path, output_file: Path) -> None:
        """파일 번역 (input → output)."""
        if not input_file.exists():
            raise FileNotFoundError(f"File not found: {input_file}")

        # 파일 읽기
        markdown = input_file.read_text(encoding="utf-8")

        # 번역
        translated = self.translate_markdown(markdown)

        # 파일 쓰기
        output_file.write_text(translated, encoding="utf-8")
