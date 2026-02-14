# 참고 자료

## 참고 오픈소스 프로젝트

| 프로젝트 | URL | 지원 플랫폼 | 참고 포인트 |
|---------|-----|-----------|------------|
| **barkr** | https://github.com/aitorres/barkr | Twitter, Mastodon, Bluesky, Discord, Telegram | READ/WRITE 모드 분리 패턴, Connection 추상화 구조 |
| **crossposter** | https://github.com/j-klawson/crossposter | Twitter, Mastodon, Bluesky | CLI 구조, macOS Keychain 기반 보안 저장, config.toml 설계 |
| **social-cross-post** | https://github.com/GanWeaving/social-cross-post | Bluesky, Mastodon, Instagram, Facebook, Twitter | 웹 UI 구현 방식, nginx 배포 가이드 |
| **Media-Manager** | https://github.com/Visualistic-Studios/Media-Manager | Discord, Twitter, Telegram, Facebook, Reddit | 예약 게시, 분석 기능, 프론트엔드 UI 설계 |
| **social-publish** | https://github.com/alexandru/social-publish | Twitter, Mastodon, Bluesky | Docker 셀프호스팅, RSS 피드 연동 |
| **Ayrshare API** | https://github.com/ayrshare/social-post-api-python | Twitter, Instagram, Facebook, LinkedIn, YouTube, TikTok 등 | API 래퍼 설계 패턴 (SaaS 유료 서비스) |

## 적용할 설계 패턴

### barkr의 ConnectionMode 패턴

각 Publisher에 READ/WRITE 모드를 도입하여 향후 SNS 모니터링(댓글, 반응 확인) 기능 확장 가능.

```python
# 예: TwitterPublisher(mode=[ConnectionMode.WRITE])
```

### crossposter의 보안 패턴

- macOS Keychain을 활용한 API 키/토큰 보안 저장
- config.toml에는 계정 정보(이름, 핸들)만 저장, 인증 정보는 Keychain에서 조회

## IndieShout의 차별점

- **SNS + 블로그 통합 크로스포스팅**: SNS 3채널 + 블로그 4채널을 하나의 도구로 동시 게시
- **다국어 자동화**: 한글 원문 → 영문 자동 번역 → 한/영 동시 게시 + 해외 블로그 크로스포스팅
- **Hugo 본진 + Canonical URL SEO 전략**: 모든 크로스포스팅이 본진 SEO에 기여
- **Buffer 하이브리드**: Buffer 3채널 + Python SNS 3채널 + Python 블로그 4채널
- 1인 개발자 마케팅에 특화된 도구
