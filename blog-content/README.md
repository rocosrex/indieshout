# blog-content 폴더 구조 가이드

블로그 콘텐츠를 폴더 단위로 관리하고 한 번에 블로그 + SNS에 게시합니다.

## 폴더 구조

```
blog-content/
  {블로그-제목}/
    content.md    # 블로그 본문 (마크다운)
    meta.md       # SNS 텍스트 + 메타데이터
    assets/       # 이미지들 (번호순: 1.jpg, 2.png, ...)
```

## meta.md 형식

```markdown
title: 블로그 포스트 제목
tags: python, automation, blog
categories: 개발, 기술
platforms: x, threads

---

SNS용 텍스트 내용입니다.
블로그 URL은 자동으로 추가됩니다.

#해시태그 #자동화
```

**필드 설명:**
- `title`: 블로그 제목 (필수)
- `tags`: 태그 (쉼표 구분)
- `categories`: 카테고리 (쉼표 구분)
- `platforms`: 게시할 SNS (x, threads)
- `---` 이후: SNS용 텍스트

## content.md 형식

일반 마크다운 파일입니다. 이미지는 `assets/` 폴더를 참조:

```markdown
# 제목

본문 내용...

![이미지 설명](assets/1.jpg)

## 섹션

더 많은 내용...
```

## 이미지

- `assets/` 폴더에 번호 순서로 저장 (1.jpg, 2.png, 3.jpg, ...)
- 자동으로 S3에 업로드되고 URL로 치환됩니다
- 지원 형식: JPG, PNG, GIF, WebP

## 게시 명령어

### Dry-run (테스트)
```bash
indieshout blog publish-folder {폴더명} --dry-run
```

### 실제 게시 (블로그 + SNS)
```bash
indieshout blog publish-folder {폴더명}
```

### 블로그만 게시
```bash
indieshout blog publish-folder {폴더명} --skip-sns
```

### SNS만 게시
```bash
indieshout blog publish-folder {폴더명} --skip-blog
```

## 예제

```bash
# 테스트 폴더로 dry-run
indieshout blog publish-folder test-post --dry-run

# 실제 게시
indieshout blog publish-folder my-first-post

# 블로그만 (SNS 건너뛰기)
indieshout blog publish-folder my-first-post --skip-sns
```

## 작동 순서

1. `content.md`, `meta.md`, `assets/` 폴더에서 콘텐츠 로드
2. 블로그에 게시 (Hugo + GitHub Pages)
   - 이미지 S3 자동 업로드
   - 한글 → 영문 자동 번역
   - Git commit & push
3. SNS에 게시 (X, Threads)
   - SNS 텍스트 + 블로그 URL
   - 설정한 플랫폼에 동시 게시

## 팁

- 폴더명은 URL에 포함되므로 영문 권장 (예: `my-first-post`)
- 이미지는 되도록 번호순으로 정리 (1.jpg, 2.png, ...)
- meta.md의 platforms 필드로 게시할 SNS 선택 가능
