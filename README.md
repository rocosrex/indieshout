# IndieShout

1인 개발자(Rex) 마케팅을 위한 SNS + 블로그 멀티 퍼블리셔 Python 도구.

## 🚀 현재 진행 상황

### ✅ 완료된 Phase

- **Phase 1**: 기본 인프라 (데이터 모델, CLI, 설정)
- **Phase 2**: X (Twitter) 연동
- **Phase 3**: Threads 연동
- **Phase 5**: Hugo 블로그 세팅
  - 배포: https://rocosrex.github.io/rex-ai-chronicles/
  - AWS S3 이미지 업로드 (rex-ai-chronicles)
- **Phase 6**: 번역 자동화 (한글 → 영문)
- **Phase 7**: 통합 및 Claude Code Skills

### 📊 통계

- **총 테스트**: 106개 (모두 통과)
- **구현된 채널**: X, Threads, Hugo 블로그
- **다국어**: 한글/영문 자동 번역
- **이미지 호스팅**: AWS S3 자동 업로드

---

## 📁 프로젝트 구조

```
indieshout/
├── src/indieshout/
│   ├── models/          # Pydantic 데이터 모델
│   ├── publishers/      # SNS 퍼블리셔 (X, Threads)
│   ├── blog/            # 블로그 퍼블리셔 (Hugo)
│   ├── formatter/       # 플랫폼별 콘텐츠 포맷 변환
│   └── utils/           # 설정, 번역, 로깅
├── blog-site/           # Hugo 블로그 (별도 저장소)
├── tests/               # 테스트 (92개)
├── config/              # 설정 파일
└── docs/                # 문서
```

---

## 🎯 주요 기능

### SNS 게시
```bash
# X (Twitter) 게시
indieshout sns post "테스트 트윗 #IndieShout" --platforms x --no-dry-run

# Threads 게시
indieshout sns post "테스트 포스트 🧵" --platforms threads --no-dry-run

# 멀티 게시 (X + Threads)
indieshout sns post "동시 게시!" --platforms x,threads --no-dry-run
```

### 블로그 게시
```python
from indieshout.blog.hugo_publisher import HugoPublisher
from indieshout.models.content import Content, ContentType

publisher = HugoPublisher(config)
content = Content(
    content_type=ContentType.BLOG,
    title="블로그 포스트",
    text="내용...",
    tags=["python", "개발"]
)
publisher.publish(content)  # 한글 + 영문 자동 생성
```

---

## 📚 문서

- [개발 계획](docs/plan.md) - Phase별 로드맵
- [아키텍처](docs/architecture.md) - 시스템 구조
- [블로그 전략](docs/blog-strategy.md) - Hugo + GitHub Pages
- [API 가이드](docs/api-guide.md) - 플랫폼별 API 등록

---

## 🔧 설치 및 실행

```bash
# 의존성 설치
uv sync

# 테스트 실행
uv run pytest tests/ -v

# CLI 실행
uv run indieshout --help
```

---

## 🌐 배포된 사이트

- **블로그**: https://rocosrex.github.io/rex-ai-chronicles/
- **X (Twitter)**: @RocosRex
- **Threads**: @blockplanet_official

---

## 📝 라이선스

MIT License

---

**Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>**
