# IndieShout 개발 계획

## Phase 1: 기본 인프라 (1주)
- [ ] 프로젝트 구조 생성
- [ ] 데이터 모델 정의 (Pydantic)
- [ ] BasePublisher / BaseBlogPublisher 추상 클래스 구현
- [ ] 설정 파일 로더 구현
- [ ] 기본 CLI 인터페이스

## Phase 2: X (Twitter) 연동 (2~3일)
- [ ] Twitter Developer Portal 앱 등록 및 API 키 발급
- [ ] tweepy 기반 TwitterPublisher 구현
- [ ] 텍스트 게시 + 이미지 첨부 테스트
- [ ] 글자수 제한 자동 처리

## Phase 3: Threads 연동 (2~3일)
- [ ] Meta Developer Portal 앱 등록
- [ ] Threads API REST 호출 구현
- [ ] OAuth 2.0 인증 흐름 구현
- [ ] 텍스트/이미지 게시 테스트

## Phase 4: YouTube 연동 (3~4일)
- [ ] Google Cloud Console 프로젝트 생성 및 API 활성화
- [ ] OAuth 2.0 인증 구현 (google-auth)
- [ ] 영상/Shorts 업로드 구현
- [ ] 제목, 설명, 태그, 썸네일 설정

## Phase 5: Hugo 블로그 세팅 (3~4일)
- [ ] Hugo 설치 및 테마 선정
- [ ] 다국어 설정 (한글/영문) — config.toml languages 설정
- [ ] GitHub Pages 연결 및 커스텀 도메인 설정 (Gabia DNS)
- [ ] GitHub Actions 자동 빌드/배포 워크플로우 작성
- [ ] S3 이미지 버킷 생성 (rex-blog-assets)
- [ ] HugoPublisher 구현: 마크다운 파일 생성 → Git commit/push 자동화

## Phase 6: 번역 자동화 (2~3일)
- [ ] Claude Code `-p` 옵션 기반 번역 구현 (translator.py)
- [ ] 한글 마크다운 → 영문 마크다운 자동 변환
- [ ] Front matter (제목, 태그 등) 자동 번역

## Phase 7: 통합 및 마무리 (2~3일)
- [ ] 멀티 퍼블리셔 오케스트레이터 완성 (SNS + 블로그 통합)
- [ ] 에러 핸들링 및 재시도 로직
- [ ] 게시 결과 리포트 (성공/실패 요약)
- [ ] README 작성 및 사용법 문서화

## Phase 8: 고도화 (선택)
- [ ] 예약 게시 기능 (APScheduler)
- [ ] 웹 UI 대시보드 (Streamlit 또는 FastAPI)
- [ ] 콘텐츠 템플릿 시스템
- [ ] 게시 이력 DB 저장 (SQLite)
- [ ] SEO 메타 태그 자동 생성 (Hugo 템플릿)
