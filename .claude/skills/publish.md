# Publish Blog Post

블로그 포스트를 작성하고 게시합니다 (한글 + 영문 자동 번역).

## Usage

```
/publish <마크다운 파일 경로>
```

또는 대화에서 직접 호출:

```
/publish
Title: 새 블로그 포스트
Tags: python, 개발
Categories: 기술

# 내용

블로그 본문...
```

## What it does

1. 한글 마크다운 파일 생성 (blog-site/content/posts/)
2. 영문으로 자동 번역
3. Git commit & push
4. GitHub Actions가 자동 빌드
5. GitHub Pages에 배포

## Implementation

```bash
# HugoPublisher로 블로그 게시
uv run python -c "
from datetime import datetime
from indieshout.blog.hugo_publisher import HugoPublisher
from indieshout.models.content import Content, ContentType
from indieshout.utils.config import load_config

config = load_config()
publisher = HugoPublisher(config)

content = Content(
    content_type=ContentType.BLOG,
    title='$TITLE',
    text='''$TEXT''',
    tags=$TAGS,
    categories=$CATEGORIES,
    date=datetime.now()
)

publisher.authenticate()
publisher.validate(content)
result = publisher.publish(content)

print(f'✅ 블로그 게시 완료!')
print(f'URL: {result[\"url\"]}')
print(f'한글: {result[\"files\"][\"ko\"]}')
print(f'영문: {result[\"files\"][\"en\"]}')
"

# blog-site로 이동해서 push
cd blog-site && git push
```

## Example

```
/publish
Title: IndieShout 개발 일지
Tags: python, automation, blog
Categories: 개발

# IndieShout 개발 일지

오늘은 블로그 자동 게시 기능을 완성했습니다!

## 주요 기능

- 한글 작성 → 영문 자동 번역
- GitHub Pages 자동 배포
- SNS 연동
```
