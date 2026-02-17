# Post to SNS

X (Twitter), Threads에 SNS 포스트를 게시합니다.

## Usage

```
/sns <텍스트> [--platforms x,threads]
```

또는 대화에서:

```
/sns "새 업데이트 출시! #IndieShout" --platforms x,threads
```

## What it does

1. 플랫폼별 포맷 변환 (X: 280자, Threads: 500자)
2. 동시에 여러 SNS에 게시
3. 결과 리포트 출력

## Implementation

```bash
# CLI로 SNS 게시
uv run indieshout sns post "$TEXT" --platforms $PLATFORMS --no-dry-run
```

## Platforms

- `x`: X (Twitter) - @RocosRex
- `threads`: Threads - @blockplanet_official
- 여러 개: `--platforms x,threads` (쉼표로 구분)

## Examples

### X만 게시
```
/sns "테스트 트윗 #Test" --platforms x
```

### Threads만 게시
```
/sns "긴 포스트 내용... (최대 500자)" --platforms threads
```

### 멀티 게시 (X + Threads)
```
/sns "동시에 여러 SNS에 게시! #IndieShout" --platforms x,threads
```

## Options

- `--platforms`: 게시할 플랫폼 (기본: 전체)
- `--image`: 이미지 첨부 (향후 지원)
- `--dry-run`: 실제 게시 안 함 (테스트용)
