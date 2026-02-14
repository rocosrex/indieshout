# 블로그 전략

## 핵심 전략

Hugo 다국어 사이트로 한/영 동시 운영 + 해외 플랫폼 크로스포스팅.
모든 크로스포스팅 글에 canonical URL을 Hugo 블로그로 지정하여 SEO 점수를 본진에 집중.

## Hugo + GitHub Pages 선택 근거

### Hugo는 빌드 도구 (블로그 사이트가 아님)

```
Hugo(엔진) → .html/.css(빌드 결과) → GitHub Pages(배포처)
```

- Hugo: 마크다운 → HTML 변환 도구 (사용자에게 보이지 않음)
- GitHub 저장소: 소스 + 빌드 결과 저장
- GitHub Pages: HTML 웹 서빙 (이것이 블로그 사이트)
- 커스텀 도메인: rex.dev (사용자 접속 URL)

### WordPress + Cloudways 대비 장점

| 항목 | WordPress + Cloudways | Hugo + GitHub Pages |
|------|:---:|:---:|
| 호스팅 | $132/년 | $0 |
| 도메인 | $10.44/년 | $10.44/년 |
| 이미지(S3) | ~$1~5/년 | ~$1~5/년 |
| 번역 | ~$1~5/년 | ~$1~5/년 |
| **연간 합계** | **~$148/년** | **~$17/년** |

연간 $130 이상 절약. 정적 사이트라 성능도 더 빠르고, 서버 관리 불필요.

### GitHub Pages 제약

- 저장소 용량 1GB 권장, 사이트 크기 1GB 제한
- 월 대역폭 100GB 소프트 리밋 (월 20만 PV 가능)
- 시간당 빌드 10회 제한
- 유료 플랜으로 업그레이드 불가 (제한 고정)

블로그 마크다운 1,000개 ≈ 10~20MB. 이미지는 S3 외부 CDN 사용하므로 용량 걱정 불필요.
월 20만 PV 초과 시 Cloudflare Pages(무료, 대역폭 무제한) 또는 Netlify/Vercel로 이전.

## 다국어 구조

```
content/posts/my-post/
  ├── index.ko.md  (한글)
  └── index.en.md  (영문)
→ https://rex.dev/ko/posts/my-post/
→ https://rex.dev/en/posts/my-post/
```

언어 전환 버튼 자동 생성, 각 언어별 RSS 피드 별도 생성.

## Canonical URL 전략

Dev.to, Hashnode, Medium에 게시 시 원본 URL을 Hugo 블로그로 지정.
구글이 Rex 도메인을 원본으로 인식 → SEO 점수 집중.

- 한/영 트래픽 합산으로 도메인 권위 빠른 상승
- 네이버 블로그 불필요: 한국 사용자도 구글 검색으로 Hugo /ko/ 페이지 노출

## 게시 워크플로우

```
Rex가 한글로 블로그 글 작성
    │
    ▼
IndieShout Python 스크립트 실행
    │
    ├── 1. 한글 마크다운 생성 → blog-site/content/posts/{slug}/index.ko.md
    ├── 2. DeepL API로 영문 번역 → blog-site/content/posts/{slug}/index.en.md
    ├── 3. 이미지가 있으면 S3 업로드 → URL 생성
    ├── 4. Git add → commit → push → GitHub Actions가 Hugo 빌드 → GitHub Pages 배포
    ├── 5. Dev.to API → 영문 게시 (canonical_url = https://rex.dev/en/posts/{slug}/)
    ├── 6. Hashnode GraphQL → 영문 게시 (canonicalUrl = https://rex.dev/en/posts/{slug}/)
    ├── 7. Medium API → 영문 게시 (canonicalUrl = https://rex.dev/en/posts/{slug}/)
    └── 8. SNS 공유 (X, Threads + Buffer 채널에 블로그 링크 공유)
```

## 이미지 관리

- Block Planet용 AWS S3 이미 사용 중
- 블로그 이미지용 버킷 추가 또는 폴더 분리 (`rex-blog-assets/posts/`)
- 서울 리전 (ap-northeast-2), 기존 AWS 계정 활용

## 수익화

- 구글 애드센스: 트래픽 충분 시 본진 블로그에 적용 (100% 본인 수익)
- 제휴 마케팅: 자유롭게 배치 가능
- Dev.to/Hashnode/Medium은 크로스포스팅 채널로만 활용

## Cloudways 해지 시 주의사항 (참고)

1. 서버 "중지"≠"삭제": 중지 상태에서도 하드웨어 할당으로 계속 과금. 완전 중단은 서버 삭제 필요
2. 애드온 별도 과금: 서버 삭제해도 유료 애드온 수동 해지 안 하면 계속 청구
3. 후불 청구: 서버 삭제/애드온 해지 후 다음 달 최종 인보이스 1건 발생
4. 계정 삭제 즉시 영구 삭제: 유예 기간 없음, 복구 불가
5. 환불 정책 없음: 3일 무료 체험만 제공

## 비용 요약

| 항목 | 업체 | 연간 비용 |
|------|------|----------|
| 도메인 (.com) | Cloudflare Registrar | ~$10.44 |
| 블로그 호스팅 | GitHub Pages | 무료 |
| SSL / CDN | GitHub Pages 내장 (Fastly) | 무료 |
| 블로그 이미지 CDN | AWS S3 | ~$1~6 |
| 번역 자동화 | DeepL API Free | 무료 |
| Dev.to / Hashnode / Medium | 각 플랫폼 | 무료 |
| Buffer (SNS 3채널) | Buffer | 무료 |
| **합계** | | **~$17/년 (약 2.3만원)** |
