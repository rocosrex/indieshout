# API 등록 가이드

Python 개발 전에 아래 개발자 포털에서 앱 등록을 먼저 완료해야 한다.

## SNS 채널

| 플랫폼 | 개발자 포털 URL | 필요 항목 |
|--------|---------------|----------|
| X (Twitter) | https://developer.twitter.com | 앱 생성 → API Key, Secret, Bearer Token |
| Threads | https://developers.facebook.com | Meta 앱 생성 → Threads API 권한 추가 |
| YouTube | https://console.cloud.google.com | 프로젝트 생성 → YouTube Data API v3 활성화 → OAuth 동의 화면 설정 |

## 번역

| 도구 | 방식 | 비용 |
|------|------|------|
| Claude Code `-p` | `subprocess.run(["claude", "-p", ...])` | 구독 포함 (추가 비용 없음) |

## 인프라 사전 준비

| 항목 | 작업 | 비용 |
|------|------|------|
| 도메인 | 기존 보유 도메인 사용 (myrestaurant.com, Gabia 관리) | 보유 중 |
| GitHub Pages | 블로그 저장소 생성 → Settings > Pages 활성화 | 무료 |
| AWS S3 버킷 | `rex-blog-assets` 버킷 생성, 퍼블릭 읽기 설정 | ~$0.05~0.50/월 |
| Hugo 설치 | `brew install hugo` (Mac) / `choco install hugo` (Windows) | 무료 |

## 플랫폼별 제약 사항

### SNS 채널

| 플랫폼 | 텍스트 제한 | 이미지 | 영상 | 특이사항 |
|--------|-----------|--------|------|---------|
| X (Twitter) | 280자 | 4장까지 | 2분 20초 | Pay-Per-Use (2026.02~ Free tier 폐지) |
| Threads | 500자 | 10장까지 | 5분 | Instagram 비즈니스 계정 필요 |
| YouTube | 제목 100자, 설명 5,000자 | 썸네일 1장 | 최대 12시간 | Shorts는 60초 이내 세로 영상 |

### 블로그 채널

| 플랫폼 | 텍스트 제한 | 이미지 | API 특이사항 |
|--------|-----------|--------|-------------|
| Hugo + GitHub Pages | 없음 | S3 CDN 외부 링크 | 저장소 1GB 권장, 사이트 1GB, 월 대역폭 100GB, 시간당 빌드 10회 |
