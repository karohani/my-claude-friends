---
name: youtube
description: YouTube 영상을 분석하여 요약, 자막, 퀴즈 생성
arguments:
  - name: url
    description: YouTube 영상 URL
    required: true
  - name: options
    description: 추가 옵션 (--quiz로 퀴즈 생성)
    required: false
---

# /youtube 명령어

YouTube 영상 URL을 입력받아 분석합니다.

## 사용법

```
/youtube [URL]           # 기본 분석 (자막 + 요약)
/youtube [URL] --quiz    # 퀴즈 포함
```

## 실행 절차

### 1. 전제 조건 확인

yt-dlp 설치 확인:
```bash
yt-dlp --version
```

설치되어 있지 않으면 안내:
```
yt-dlp가 필요합니다. 다음 명령어로 설치해주세요:
brew install yt-dlp
# 또는
pip install yt-dlp
```

### 2. URL 검증

유효한 YouTube URL 형식:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/watch?v=VIDEO_ID`

### 3. 메타데이터 추출

```bash
yt-dlp --print "%(title)s|||%(channel)s|||%(upload_date)s|||%(duration_string)s" --no-download "URL"
```

### 4. 자막 추출

Task 도구로 `transcript-extractor` 에이전트 실행

### 5. 고유명사 교정

Task 도구로 `proper-noun-corrector` 에이전트 실행

### 6. 요약 생성

Task 도구로 `summary-generator` 에이전트 실행

### 7. 퀴즈 생성 (--quiz 옵션 시)

Task 도구로 `quiz-generator` 에이전트 실행

### 8. 파일 저장

저장 경로: `./youtube/{channel-name}/{YYYY-MM-DD}-{title}.md`

채널명과 제목 정제:
- 특수문자 제거
- 공백을 하이픈으로 변환
- 소문자 변환

### 9. 정리

임시 VTT 파일 삭제:
```bash
rm -f *.vtt
```

## 출력 예시

```
YouTube 영상 분석을 시작합니다.

제목: [영상 제목]
채널: [채널명]
길이: [00:00:00]

[1/4] 자막 추출 중... 완료 (한국어 수동 자막)
[2/4] 고유명사 교정 중... 완료 (12개 교정)
[3/4] 요약 생성 중... 완료
[4/4] 퀴즈 생성 중... 완료

저장 완료: ./youtube/channel-name/2024-01-15-video-title.md
```

## 에러 메시지

| 상황 | 메시지 |
|------|--------|
| yt-dlp 미설치 | "yt-dlp가 설치되어 있지 않습니다." |
| 잘못된 URL | "올바른 YouTube URL을 입력해주세요." |
| 자막 없음 | "이 영상에는 사용 가능한 자막이 없습니다." |
| 네트워크 오류 | "영상에 접근할 수 없습니다. URL과 네트워크를 확인해주세요." |
