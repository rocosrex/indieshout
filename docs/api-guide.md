# API 등록 가이드

Python 개발 전에 아래 개발자 포털에서 앱 등록을 먼저 완료해야 한다.

## SNS 채널

| 플랫폼 | 개발자 포털 URL | 필요 항목 |
|--------|---------------|----------|
| X (Twitter) | https://developer.twitter.com | 앱 생성 → API Key, Secret, Bearer Token |
| Threads | https://developers.facebook.com | Meta 앱 생성 → Threads API 권한 추가 |
| YouTube | https://console.cloud.google.com | 프로젝트 생성 → YouTube Data API v3 활성화 → OAuth 동의 화면 설정 |

## 블로그 채널

| 플랫폼 | API 키 발급 위치 | 필요 항목 |
|--------|----------------|----------|
| Dev.to | https://dev.to/settings/extensions | API Keys 섹션에서 생성 |
| Hashnode | https://hashnode.com/settings/developer | Personal Access Token 생성 |
| Medium | https://medium.com/me/settings/security | Integration tokens 생성 |
| DeepL (번역) | https://www.deepl.com/pro-api | DeepL API Free 가입 → Authentication Key 발급 |

## 인프라 사전 준비

| 항목 | 작업 | 비용 |
|------|------|------|
| 도메인 등록 | Cloudflare Registrar에서 .com 도메인 구매 | ~$10.44/년 |
| GitHub Pages | 블로그 저장소 생성 → Settings > Pages 활성화 | 무료 |
| AWS S3 버킷 | `rex-blog-assets` 버킷 생성, 퍼블릭 읽기 설정 | ~$0.05~0.50/월 |
| Hugo 설치 | `brew install hugo` (Mac) / `choco install hugo` (Windows) | 무료 |

## 플랫폼별 제약 사항

### SNS 채널

| 플랫폼 | 텍스트 제한 | 이미지 | 영상 | 특이사항 |
|--------|-----------|--------|------|---------|
| X (Twitter) | 280자 (무료) | 4장까지 | 2분 20초 | 무료 API: 월 1,500 트윗 |
| Threads | 500자 | 10장까지 | 5분 | Instagram 비즈니스 계정 필요 |
| YouTube | 제목 100자, 설명 5,000자 | 썸네일 1장 | 최대 12시간 | Shorts는 60초 이내 세로 영상 |

### 블로그 채널

| 플랫폼 | 텍스트 제한 | 이미지 | API 특이사항 |
|--------|-----------|--------|-------------|
| Hugo + GitHub Pages | 없음 | S3 CDN 외부 링크 | 저장소 1GB 권장, 사이트 1GB, 월 대역폭 100GB, 시간당 빌드 10회 |
| Dev.to | 없음 | 외부 URL 참조 | canonical_url 파라미터 지원. 게시 + 수정 가능 |
| Hashnode | 없음 | 외부 URL 참조 | canonicalUrl 필드 지원. GraphQL mutation으로 게시 + 수정 |
| Medium | 없음 | 외부 URL 참조 | canonicalUrl 파라미터 지원. 게시만 가능 (수정 API 없음) |
