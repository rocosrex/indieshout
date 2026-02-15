# 사전 작업 체크리스트

개발 시작 전 Rex가 직접 완료해야 할 작업 목록.

---

## 1. 인프라 설정

- [x] **도메인** — 기존 보유 도메인 사용: `myrestaurant.com` (Gabia 관리, 구매 불필요)
- [ ] **Gabia DNS 설정** — GitHub Pages 연결을 위한 DNS 레코드 추가
  - A 레코드: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
  - CNAME 레코드: `www` → GitHub Pages 주소
- [ ] **GitHub 블로그 저장소 생성** — 저장소 생성 후 Settings > Pages 활성화 (무료)
- [ ] **AWS S3 버킷 생성** — [AWS Console](https://console.aws.amazon.com/s3)
  - 버킷명: `rex-blog-assets`
  - 리전: `ap-northeast-2` (서울)
  - 퍼블릭 읽기 설정
- [ ] **Hugo 설치** — `brew install hugo` (무료)

---

## 2. SNS API 키 발급

### X (Twitter) — 유료 (Pay-Per-Use)
- [ ] https://developer.twitter.com 접속
- [ ] 앱 생성
- [ ] 발급 항목: API Key, API Secret, Access Token, Access Token Secret
- [ ] Pay-Per-Use 크레딧 구매 (크레딧 미리 충전, API 호출마다 차감)
- [ ] ⚠️ 2026년 2월부터 Free tier 폐지, 종량제로 전환됨
- [ ] 참고: 기존 Free 사용자에게 일회성 $10 바우처 지급

### Threads
- [ ] https://developers.facebook.com 접속
- [ ] Meta 앱 생성
- [ ] Threads API 권한 추가
- [ ] OAuth 2.0 Long-Lived Token 발급
- [ ] 참고: Instagram 비즈니스 계정 필요

### YouTube
- [ ] https://console.cloud.google.com 접속
- [ ] 프로젝트 생성
- [ ] YouTube Data API v3 활성화
- [ ] OAuth 동의 화면 설정
- [ ] 발급 항목: Client ID, Client Secret

---

## 3. 번역

- [x] **Claude Code `-p` 옵션 사용** — 기존 Claude Code 구독에 포함, 추가 API 키 불필요

---

## 4. Buffer 설정

- [ ] https://buffer.com 가입 (무료 플랜)
- [ ] LinkedIn 계정 연결
- [ ] Instagram 계정 연결
- [ ] Facebook 계정 연결

---

## 5. 계정 가입 (없는 경우)

- [ ] GitHub
- [ ] AWS

- [ ] X (Twitter)
- [ ] Instagram (비즈니스 계정 전환)
- [ ] YouTube (Google 계정)

---

## 발급 후 할 일

발급받은 키/토큰을 프로젝트 루트의 `.env` 파일에 저장:

```bash
# SNS
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_TOKEN_SECRET=xxx
THREADS_APP_ID=xxx
THREADS_APP_SECRET=xxx
THREADS_ACCESS_TOKEN=xxx
YOUTUBE_CLIENT_ID=xxx
YOUTUBE_CLIENT_SECRET=xxx

# AWS
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
S3_BUCKET_NAME=rex-blog-assets
S3_REGION=ap-northeast-2
```

> `.env` 파일은 `.gitignore`에 반드시 포함할 것.
