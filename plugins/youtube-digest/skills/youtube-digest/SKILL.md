---
name: youtube-digest
description: This skill should be used when the user asks to "summarize youtube", "youtube 요약", "analyze video", "영상 분석", "extract transcript", "자막 추출", "youtube digest", or provides a YouTube URL. Extracts subtitles, corrects proper nouns, generates summary and optional quiz.
version: 1.0.0
user-invocable: true
arguments:
  - name: url
    description: YouTube video URL
    required: true
  - name: quiz
    description: Generate learning quiz (--quiz flag)
    required: false
---

# YouTube Digest Skill

YouTube 영상을 분석하여 마크다운 문서로 정리하는 워크플로우입니다.

## 전제 조건

yt-dlp가 설치되어 있어야 합니다:
```bash
brew install yt-dlp
# 또는
pip install yt-dlp
```

## 워크플로우

### Phase 1: 메타데이터 및 자막 추출

1. **URL 검증**: YouTube URL 형식 확인 (youtube.com/watch, youtu.be)

2. **메타데이터 추출** (yt-dlp 사용):
   ```bash
   yt-dlp --print "%(title)s|||%(channel)s|||%(upload_date)s|||%(duration_string)s" --no-download "URL"
   ```

3. **자막 추출** - 우선순위:
   - 1순위: 수동 한국어 자막 (`ko`)
   - 2순위: 수동 영어 자막 (`en`)
   - 3순위: 자동 생성 한국어 자막 (`ko-auto`)
   - 4순위: 자동 생성 영어 자막 (`en-auto`)

   ```bash
   # 사용 가능한 자막 확인
   yt-dlp --list-subs --no-download "URL"

   # 자막 다운로드 (예: 한국어)
   yt-dlp --write-sub --sub-lang ko --skip-download --output "%(id)s" "URL"
   # 또는 자동 생성 자막
   yt-dlp --write-auto-sub --sub-lang ko --skip-download --output "%(id)s" "URL"
   ```

4. **자막 파일 파싱**: VTT 파일에서 텍스트 추출, 타임스탬프 정리

### Phase 2: 고유명사 교정

Task 도구로 `proper-noun-corrector` 에이전트 실행:
- 자막에서 고유명사, 기술 용어, 브랜드명 추출
- WebSearch로 정확한 철자 확인
- 일관성 있게 교정 적용

### Phase 3: 요약 및 인사이트 생성

Task 도구로 `summary-generator` 에이전트 실행:
- 3-5문장 요약
- 핵심 인사이트 3-5개
- 섹션별 구분 (가능한 경우)

### Phase 4: 퀴즈 생성 (선택)

`--quiz` 플래그가 있는 경우, Task 도구로 `quiz-generator` 에이전트 실행:
- 기초 문제 3개
- 중급 문제 3개
- 고급 문제 3개

### Phase 5: 마크다운 저장

저장 경로: `./youtube/{channel-name}/{YYYY-MM-DD}-{sanitized-title}.md`

## 출력 형식

```markdown
---
title: "[제목]"
source: "[채널명]"
url: "[URL]"
duration: "[영상 길이]"
date_processed: "[처리 날짜]"
original_language: "[원본 자막 언어]"
---

# [제목]

> 출처: [채널명](채널URL) | 길이: [영상 길이] | [업로드 날짜]

## 요약

[3-5문장으로 영상 내용 요약]

## 핵심 인사이트

- **[인사이트 1 제목]**: [설명]
- **[인사이트 2 제목]**: [설명]
- **[인사이트 3 제목]**: [설명]

## 전체 스크립트

[타임스탬프 포함 교정된 전체 스크립트]

## 학습 퀴즈

### 기초 (Basic)
1. [문제]
   - A) [선택지]
   - B) [선택지]
   - C) [선택지]
   - D) [선택지]
   <details><summary>정답</summary>B) [정답 및 설명]</details>

### 중급 (Intermediate)
[...]

### 고급 (Advanced)
[...]
```

## 에러 처리

- **자막 없음**: "이 영상에는 사용 가능한 자막이 없습니다. 음성 인식 도구를 사용하거나 수동으로 스크립트를 입력해주세요."
- **URL 오류**: "올바른 YouTube URL을 입력해주세요. 예: https://youtube.com/watch?v=xxxxx"
- **yt-dlp 없음**: "yt-dlp가 설치되어 있지 않습니다. `brew install yt-dlp` 또는 `pip install yt-dlp`로 설치해주세요."

## 임시 파일 정리

작업 완료 후 다운로드된 .vtt 파일 삭제:
```bash
rm -f *.vtt
```
