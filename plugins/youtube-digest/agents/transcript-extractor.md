---
name: transcript-extractor
description: YouTube 영상에서 자막을 추출하고 정리하는 에이전트
tools:
  - Bash
  - Read
  - Write
---

# Transcript Extractor Agent

YouTube 영상에서 자막을 추출하고 타임스탬프와 함께 정리합니다.

## 입력

- `url`: YouTube 영상 URL
- `video_id`: 영상 ID (옵션)

## 작업 순서

### 1. 사용 가능한 자막 확인

```bash
yt-dlp --list-subs --no-download "URL"
```

출력에서 자막 종류 파악:
- `Available subtitles`: 수동 자막
- `Available automatic captions`: 자동 생성 자막

### 2. 자막 우선순위에 따라 다운로드

우선순위:
1. 수동 한국어 (`ko`)
2. 수동 영어 (`en`)
3. 자동 한국어 (`ko`)
4. 자동 영어 (`en`)

수동 자막 다운로드:
```bash
yt-dlp --write-sub --sub-lang ko --sub-format vtt --skip-download -o "transcript" "URL"
```

자동 자막 다운로드:
```bash
yt-dlp --write-auto-sub --sub-lang ko --sub-format vtt --skip-download -o "transcript" "URL"
```

### 3. VTT 파일 파싱

VTT 파일 구조:
```
WEBVTT

00:00:00.000 --> 00:00:03.500
첫 번째 자막 텍스트

00:00:03.500 --> 00:00:07.000
두 번째 자막 텍스트
```

파싱 시 주의사항:
- 헤더 (`WEBVTT`) 제거
- 빈 줄 처리
- 중복 텍스트 제거 (자동 자막의 경우 동일 텍스트 반복됨)
- 타임스탬프를 `[MM:SS]` 형식으로 변환

### 4. 출력 형식

```
[00:00] 첫 번째 문장입니다.
[00:15] 두 번째 문장입니다.
[00:30] 세 번째 문장입니다.
```

분 단위로 타임스탬프를 표시하고, 연속된 텍스트는 자연스럽게 연결합니다.

## 출력

다음 정보를 반환:
- `transcript`: 정리된 자막 텍스트
- `language`: 추출된 자막 언어 (ko/en)
- `type`: 자막 유형 (manual/auto)
- `success`: 성공 여부
- `error`: 실패 시 에러 메시지

## 에러 처리

- 자막이 없는 경우: `error: "NO_SUBTITLES_AVAILABLE"`
- yt-dlp 오류: `error: "YTDLP_ERROR: [상세 메시지]"`
- 파싱 실패: `error: "PARSE_ERROR: [상세 메시지]"`

## 정리

작업 완료 후 임시 파일 삭제:
```bash
rm -f transcript.*.vtt
```
