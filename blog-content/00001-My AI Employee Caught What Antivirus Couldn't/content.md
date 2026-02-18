# Windows PC 애드웨어 정리 기록 (2026.02.15)

## 서두

Edge 브라우저를 실행하면 가끔씩 광고 사이트가 갑자기 나타나는 문제가 있었다. 애드웨어일 것으로 추정은 했지만, 백신 프로그램으로도 잘 잡히지 않았다.

그래서 Claude Code에게 할 수 있는지 물었더니, 할 수 있다고 해서 진행해 보았다. 여러 애드웨어를 잡아냈고, 잡아내는 과정에서 Claude Code는 작업관리자로 볼 수 있는 프로세스도 조사하고, 레지스트리도 조사하면서 삭제를 진행했다. 그러면서 마지막으로 정리가 안 되는 놈은 리부팅 후 자동으로 정리되도록 해놓고, 나한테 리부팅하라고 한다.

시키는 대로 했더니 정말 잘 된다. ㅎㅎㅎ 참 대단한 놈이다. 이걸 내가 직접 하려면 어휴~~ 얼마나 많은 시간을 보냈을지 상상도 안 간다. 인터넷에서 검색해 봐야 자기네 백신이니 클리너를 설치하라고만 하는데, 설치해도 되지도 않고, 돈 내라고 하고, 짜증만 났을 텐데… 아무튼 Claude Code는 참 사랑스럽다.

아래 내용은 모든 일을 다 한 후에, 나에게 보고한 내용이다. 와우~~ 아주 똑똑한 직원 하나 생긴 느낌이다.

---

## 발단

작업관리자를 살펴보다가 `clipdown.exe`라는 정체불명의 프로세스가 **141MB**나 메모리를 차지하고 있는 것을 발견했다. 조사해보니 이것 말고도 숨어있는 애드웨어가 더 있었다.

---

## 제거한 애드웨어 목록

### 1. clipdown (클립다운)

| 항목 | 내용 |
|------|------|
| 프로세스 | `clipdown.exe`, `cdsrvc.exe` |
| 경로 | `C:\Program Files (x86)\clipdown\` |
| 제작사 | J's Future |
| 메모리 | 141MB |
| 정체 | YouTube 영상/음원 다운로더 |

**수상한 점:**
- `inject_script.txt` (140KB) — 스크립트 삽입용 파일
- `ad_config.xml`, `ad_shortcutbookmark.xml` — 광고 설정 파일
- `yab_script.txt` — 추가 스크립트
- 별도 백그라운드 서비스(`cdsrvc.exe`)가 항상 실행
- `ffmpeg.exe`, `yt-dlp_x86.exe`, `aria2c.exe` 등 다운로드 도구 번들

**제거 방법:** 프로세스 종료 후 설치 폴더 내 `uninst.exe` 실행

---

### 2. tabservicepack

| 항목 | 내용 |
|------|------|
| 프로세스 | `tabservicepack.exe` |
| 경로 | `C:\Program Files (x86)\TabService\` |
| 제작사 | 없음 (미표기) |
| 메모리 | 15MB |
| 정체 | 광고 애드웨어 |

**수상한 점:**
- 회사명이 아예 없음
- `ad_config.xml`, `ad_shortcutbookmark.xml` — clipdown과 동일한 광고 파일 구조
- 언인스톨러 없음

**제거 방법:** 프로세스 종료 후 설치 폴더 수동 삭제

---

### 3. ToDiskService (투디스크)

| 항목 | 내용 |
|------|------|
| 프로세스 | `ToDiskService.exe` |
| 경로 | `C:\Program Files (x86)\ToDisk.com\` |
| 제작사 | 없음 (미표기) |
| 메모리 | 5MB (서비스 상주) |
| 정체 | 파일 다운로더 + 광고 애드웨어 |

**수상한 점:**
- 회사명, 설명 모두 없음
- `ToDiskDown.exe`, `ToDiskUp.exe` — 다운로드/업로드 도구
- `avcodec`, `avformat`, `avutil` 등 ffmpeg 코덱 라이브러리 다수 포함
- `detect.exe`, `detect_service.exe` — 탐지 관련 실행파일
- `HGrid.dll`, `btf*.dll` — 번들웨어 특징
- `downloader.exe` — 추가 다운로더
- `바로가기.url` — 웹사이트 유도 바로가기

**제거 방법:** 프로세스 종료 후 `Uninstall.exe /S` 실행, 잔여 폴더 수동 삭제

---

## 공통 패턴

이 세 애드웨어는 공통적인 특징을 갖고 있었다:

1. **광고 설정 파일** — `ad_config.xml`, `ad_shortcutbookmark.xml` 등
2. **미디어 코덱 번들** — ffmpeg, avcodec 등을 자체 내장
3. **백그라운드 상주** — 부팅 시 자동 실행되어 항상 메모리 점유
4. **제작사 불명확** — 회사명이 없거나 검증이 안 되는 제작사
5. **스크립트 삽입** — 웹 브라우저에 광고를 주입하는 구조

---

## 참고: 함께 확인한 정상 프로세스

조사 과정에서 정체가 불분명했지만 정상으로 확인된 프로세스들:

| 프로세스 | 정체 |
|----------|------|
| `pennyroyal.exe` | YettieSoft 피싱방지 엔진 (Anti Phishing) |
| `Goji.exe` | VestCert 관련 보안 서비스 |
| `mmgaserver.exe` | Microsoft Windows MMGA Server |
| `aimgr.exe` | Microsoft 365 AI Manager |
| `ddm.exe` | Dell Display Manager |
| `IMGSF50Svc.exe` | MarkAny Image SAFER 5.0 (DRM) |
| `natsvc.exe` | NeoNTech 네트워크 서비스 |
| `OneMarkService.exe` | NeuxLab OneMark (OneNote 확장) |
| `crashhelper.exe` | Mozilla Firefox 크래시 리포터 |
| `oCamTask.exe` | oh!soft oCam 화면녹화 |

---

## 교훈

- 작업관리자를 주기적으로 확인하자. 모르는 프로세스가 있으면 바로 조사할 것.
- 한국 무료 다운로드 프로그램은 애드웨어가 같이 설치되는 경우가 많다.
- `ad_config.xml` 같은 파일이 설치 폴더에 있으면 높은 확률로 광고 프로그램이다.
- 언인스톨러가 없는 프로그램은 더 의심해야 한다.