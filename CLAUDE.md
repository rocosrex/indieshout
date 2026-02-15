# IndieShout

1인 개발자(Rex) 마케팅을 위한 SNS + 블로그 멀티 퍼블리셔 Python 도구.

## 프로젝트 구조

- `src/publishers/` — SNS 퍼블리셔 (X, Threads, YouTube)
- `src/blog/` — 블로그 퍼블리셔 (Hugo) + 번역 자동화
- `src/models/` — Pydantic 데이터 모델
- `src/formatter/` — 플랫폼별 콘텐츠 포맷 변환
- `src/utils/` — 인증, S3 업로드, 로깅
- `blog-site/` — Hugo 블로그 저장소 (한/영 다국어)
- `config/` — 설정 파일 (API 키는 환경변수 또는 .env 사용)

## 채널 구성 (총 7채널)

- **Buffer (3)**: LinkedIn, Instagram, Facebook
- **Python SNS (3)**: X (Twitter), Threads, YouTube
- **Python 블로그 (1)**: Hugo+GitHub Pages (본진)

## 핵심 전략

- Hugo 블로그가 본진. SNS에서 블로그 링크를 공유하여 트래픽 유입
- 한글 원문 → Claude Code `-p` 옵션으로 영문 자동 번역 → 한/영 동시 게시 (추가 비용 없음)
- 블로그 이미지는 AWS S3 (`rex-blog-assets` 버킷) 사용

## 사용자 인터페이스

| 인터페이스 | 명령 | 용도 |
|-----------|------|------|
| **CLI** | `indieshout blog publish <file>` | 블로그 게시 (번역 + 배포 + SNS 공유) |
| **CLI** | `indieshout sns post <text>` | SNS 전용 게시 |
| **Claude Code Skill** | `/publish <file>` | 대화에서 블로그 게시 |
| **Claude Code Skill** | `/sns <text>` | 대화에서 SNS 게시 |
| **Telegram** | OpenClaw pio에게 메시지 | SNS 게시 (향후 개발) |

## 기술 스택

- Python 3.11+, pip + pyproject.toml
- httpx, pydantic, pyyaml, tweepy, boto3, gitpython
- Hugo (정적 사이트 생성), GitHub Pages (호스팅), GitHub Actions (CI/CD)

## 빌드 & 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 테스트 실행
pytest tests/

# Hugo 로컬 서버 (블로그 미리보기)
cd blog-site && hugo server -D

# Hugo 빌드
cd blog-site && hugo --minify
```

## 코드 스타일

- Python: PEP 8, type hints 사용
- 추상 클래스: `BasePublisher` (SNS), `BaseBlogPublisher` (블로그)
- 설정: YAML 기반, 민감 정보는 환경변수 (.env)
- 에러 처리: 각 퍼블리셔별 독립적 try/except, 하나 실패해도 나머지 계속 실행

## 프로젝트 문서

작업 전 관련 문서를 먼저 읽고 진행할 것:

| 문서 | 경로 | 내용 |
|------|------|------|
| 개발 계획 | `docs/plan.md` | 개발 로드맵, Phase별 체크리스트 |
| 아키텍처 | `docs/architecture.md` | 채널 구성, 기술 스택 상세, 프로젝트 구조, 데이터 모델, 설정 파일 |
| 블로그 전략 | `docs/blog-strategy.md` | 블로그 플랫폼 선정 근거, 비용 분석, 게시 워크플로우, SEO 전략 |
| API 가이드 | `docs/api-guide.md` | 플랫폼별 API 등록 방법, 인증 방식, 제약 사항 |
| 참고 자료 | `docs/references.md` | 참고 오픈소스 프로젝트, 적용할 설계 패턴 |
