# 아키텍처

## 운영 방식

- **Buffer 무료 플랜 (3채널)**: 인증이 까다로운 SNS 플랫폼 담당
- **Python 자체 개발 — SNS (3채널)**: API 접근이 용이하거나 Buffer가 지원하지 않는 플랫폼 담당
- **Python 자체 개발 — 블로그 (4채널)**: Hugo 본진 블로그 + 해외 블로그 크로스포스팅
- **다국어 지원**: 한글 원문 → 영문 자동 번역 → 한/영 동시 게시

## 채널 상세

### Buffer SNS 채널 (3개)

| # | SNS | 용도 | Buffer 선택 이유 |
|---|-----|------|-----------------|
| 1 | **LinkedIn** | B2B 네트워킹, 기업 파트너십, 전문성 어필 | 앱 심사가 가장 까다로움. Buffer 로그인만으로 해결 |
| 2 | **Instagram** | 꽃/식물 매크로 사진, 게임 스크린샷, 비주얼 콘텐츠 | 비즈니스 계정 + Graph API 설정 복잡. Buffer가 잘 지원 |
| 3 | **Facebook** | 커뮤니티 공유, 폭넓은 도달 | Graph API 권한 관리 번거로움. Instagram과 같은 Meta 계열 |

### Python SNS 채널 (3개)

| # | SNS | 용도 | Python 선택 이유 | 개발 난이도 |
|---|-----|------|-----------------|------------|
| 1 | **X (Twitter)** | 개발 일지, 기술 팁, 빠른 업데이트 | `tweepy` + 무료 API tier로 가장 쉬움 | ★★☆ |
| 2 | **Threads** | Instagram 연동, 캐주얼 텍스트 콘텐츠 | Meta가 2024년 API 공개. REST 호출로 비교적 단순 | ★★☆ |
| 3 | **YouTube** | Shorts, 게임 플레이, 개발 브이로그 | 영상 업로드는 Buffer로도 제한적. 직접 제어가 유연 | ★★☆ |

### Python 블로그 채널 (4개)

| # | 블로그 | 역할 | API 방식 | 비용 | 개발 난이도 |
|---|--------|------|---------|------|------------|
| 1 | **Hugo + GitHub Pages** | 🏠 **본진 블로그** (한/영 다국어) | Git push → GitHub Actions 자동 빌드/배포 | 도메인만 ~$10.44/년 | ★★☆ |
| 2 | **Dev.to** | 크로스포스팅 (영문) | REST API (게시/수정 지원) | 무료 | ★☆☆ |
| 3 | **Hashnode** | 크로스포스팅 (영문) | GraphQL API (게시/수정 지원) | 무료 | ★★☆ |
| 4 | **Medium** | 크로스포스팅 (영문) | REST API (게시만, 수정 미지원) | 무료 | ★☆☆ |

### 제외된 채널

| 플랫폼 | 제외 사유 |
|--------|----------|
| **네이버 블로그** | 공식 API 없음, 봇 탐지 → 계정 제재 리스크. 구글 SEO 효과 없음. 필요 시 수동 게시 |
| **Velog** | 게시 API 미제공. 수익화 불가 (광고 수익 100% Velog가 가져감) |
| **티스토리** | 카카오 운영 (사용 거부). 카카오 자체 광고 강제 삽입 |

## 기술 스택

### SNS API

| 플랫폼 | API | Python 라이브러리 | 인증 방식 | 비고 |
|--------|-----|------------------|----------|------|
| X (Twitter) | X API v2 | `tweepy` | OAuth 2.0 | 무료 tier: 월 1,500 트윗 |
| Threads | Threads API | `httpx` REST 직접 호출 | OAuth 2.0 (Meta) | 2024년 공개 API |
| YouTube | YouTube Data API v3 | `google-api-python-client` | OAuth 2.0 (Google) | 영상/Shorts 업로드 |

### 블로그 API

| 플랫폼 | API | 방식 | 인증 | 비고 |
|--------|-----|------|------|------|
| Hugo + GitHub Pages | Git CLI / GitHub API | 마크다운 → `git push` → GitHub Actions 빌드 | SSH Key 또는 PAT | 한/영 다국어 |
| Dev.to | REST API | `httpx` POST/PUT | API Key (헤더) | 게시 + 수정 지원 |
| Hashnode | GraphQL API | `httpx` POST (GraphQL) | Personal Access Token | 게시 + 수정 지원 |
| Medium | REST API | `httpx` POST | Integration Token | 게시만 (수정 미지원) |

### 공통 라이브러리

- `httpx`: HTTP 요청
- `pydantic`: 데이터 모델 정의 및 검증
- `pyyaml`: 설정 파일 관리
- `boto3`: AWS S3 이미지 업로드
- `gitpython`: Git 커밋/푸시 자동화
- `apscheduler`: 예약 게시 (선택)
- `rich` / `click`: CLI 인터페이스 (선택)
- `pillow`: 이미지 리사이징/포맷 변환 (선택)

### 번역 자동화 (한글 → 영문)

- **DeepL API Free**: 무료 (50만자/월, 블로그 글 월 250편 분량) — 1차 선택
- **Claude API (Sonnet)**: ~$0.003~0.01/글 — 기술 글 번역 품질 우수, 대안
- **Google Translate API**: $20/100만자 — 비상용

## 프로젝트 구조

```
indieshout/
├── config/
│   ├── config.yaml              # API 키, 토큰, 계정 설정
│   └── config.example.yaml      # 예시 설정 파일 (키 제외)
├── src/
│   ├── __init__.py
│   ├── main.py                  # 엔트리 포인트 (CLI)
│   ├── models/
│   │   ├── __init__.py
│   │   └── content.py           # 콘텐츠 데이터 모델
│   ├── publishers/
│   │   ├── __init__.py
│   │   ├── base.py              # 추상 베이스 클래스 (Publisher)
│   │   ├── twitter.py           # X (Twitter) 게시
│   │   ├── threads.py           # Threads 게시
│   │   └── youtube.py           # YouTube 업로드
│   ├── blog/
│   │   ├── __init__.py
│   │   ├── base.py              # 추상 베이스 클래스 (BlogPublisher)
│   │   ├── hugo.py              # Hugo 마크다운 생성 + Git push 배포
│   │   ├── devto.py             # Dev.to REST API 게시
│   │   ├── hashnode.py          # Hashnode GraphQL API 게시
│   │   ├── medium.py            # Medium REST API 게시
│   │   └── translator.py        # 한글 → 영문 번역 자동화
│   ├── formatter/
│   │   ├── __init__.py
│   │   └── content_formatter.py # 플랫폼별 콘텐츠 포맷 변환
│   └── utils/
│       ├── __init__.py
│       ├── auth.py              # OAuth 토큰 관리 및 갱신
│       ├── s3_uploader.py       # AWS S3 이미지 업로드
│       └── logger.py            # 로깅 설정
├── blog-site/                   # Hugo 블로그 저장소
│   ├── content/posts/{slug}/
│   │   ├── index.ko.md          # 한글 버전
│   │   └── index.en.md          # 영문 버전
│   ├── static/
│   ├── themes/
│   └── config.toml              # Hugo 설정 (다국어 포함)
├── tests/
├── docs/
├── CLAUDE.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 핵심 설계

### 콘텐츠 데이터 모델

```python
from pydantic import BaseModel
from typing import Optional

class Content(BaseModel):
    text: str                              # 본문 텍스트
    image_paths: Optional[list[str]] = None  # 이미지 파일 경로
    video_path: Optional[str] = None        # 영상 파일 경로
    tags: Optional[list[str]] = None        # 해시태그
    platforms: list[str]                    # 게시 대상 플랫폼 목록
    title: Optional[str] = None            # YouTube/블로그용 제목
    scheduled_at: Optional[str] = None     # 예약 게시 시간 (ISO 8601)
```

### Publisher 추상 클래스

```python
from abc import ABC, abstractmethod
from models.content import Content

class BasePublisher(ABC):
    @abstractmethod
    def authenticate(self) -> bool:
        """인증 수행 및 토큰 검증"""
        pass

    @abstractmethod
    def format_content(self, content: Content) -> dict:
        """플랫폼에 맞게 콘텐츠 변환"""
        pass

    @abstractmethod
    def publish(self, content: Content) -> dict:
        """게시 실행 후 결과 반환"""
        pass

    @abstractmethod
    def validate(self, content: Content) -> bool:
        """게시 전 유효성 검사"""
        pass
```

### 멀티 퍼블리셔 오케스트레이터

```python
class IndieShout:
    def __init__(self, config: dict):
        self.publishers = {}
        # config에 따라 활성 publisher 초기화

    def publish_all(self, content: Content) -> dict:
        results = {}
        for platform in content.platforms:
            publisher = self.publishers.get(platform)
            if publisher is None:
                results[platform] = {'status': 'skipped', 'reason': 'not configured'}
                continue
            try:
                if publisher.validate(content):
                    result = publisher.publish(content)
                    results[platform] = {'status': 'success', **result}
                else:
                    results[platform] = {'status': 'failed', 'reason': 'validation error'}
            except Exception as e:
                results[platform] = {'status': 'error', 'reason': str(e)}
        return results
```

## 설정 파일 형식 (config.yaml)

```yaml
# === SNS 채널 API 설정 ===
twitter:
  api_key: "YOUR_API_KEY"
  api_secret: "YOUR_API_SECRET"
  access_token: "YOUR_ACCESS_TOKEN"
  access_token_secret: "YOUR_ACCESS_TOKEN_SECRET"

threads:
  app_id: "YOUR_APP_ID"
  app_secret: "YOUR_APP_SECRET"
  access_token: "YOUR_LONG_LIVED_TOKEN"

youtube:
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"

# === 블로그 채널 설정 ===
hugo:
  blog_repo_path: "./blog-site"
  content_dir: "content/posts"
  base_url: "https://rex.dev"
  languages: ["ko", "en"]
  default_language: "ko"
  git_remote: "origin"
  git_branch: "main"

devto:
  api_key: "YOUR_DEVTO_API_KEY"

hashnode:
  token: "YOUR_HASHNODE_TOKEN"
  publication_id: "YOUR_PUBLICATION_ID"

medium:
  integration_token: "YOUR_MEDIUM_TOKEN"

# === 이미지 CDN (AWS S3) ===
s3:
  bucket_name: "rex-blog-assets"
  region: "ap-northeast-2"
  prefix: "posts/"

# === 번역 설정 ===
translator:
  provider: "deepl"
  deepl_api_key: "YOUR_DEEPL_API_KEY"
  source_lang: "ko"
  target_lang: "en"

# === 기본 설정 ===
defaults:
  tags: ["gamedev", "indiedev", "unity3d"]
  language: "ko"
```
