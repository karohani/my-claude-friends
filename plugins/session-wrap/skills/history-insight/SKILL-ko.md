---
name: history-insight
description: This skill should be used when the user asks to "analyze history", "히스토리 분석", "session history", "세션 기록", "past sessions", "이전 세션", "capture insights", "find patterns", or wants to extract insights from Claude Code session history files.
version: 1.0.0
user-invocable: true
---

# History Insight Skill

Claude Code 세션 히스토리에서 인사이트를 추출한다.

## Trigger

- `/history-insight`
- "세션 히스토리 분석해줘"
- "capture session history"
- "save session data"

## Purpose

Claude Code 세션 히스토리에 접근하여 리뷰, 요약 또는 참조를 위해 분석한다.

## Workflow

### Step 1: 범위 결정

사용자에게 질문:
- 현재 프로젝트만?
- 모든 세션?
- 특정 날짜 범위?

### Step 2: 세션 파일 찾기

세션 파일 검색:

```bash
# 세션 파일 위치
~/.claude/projects/

# 파일은 .jsonl 형식, 디렉토리 경로로 인코딩됨
```

### Step 3: 세션 처리

파일 수에 따라 처리 방식 조정:

**1-3개 파일**: 직접 로드, 인라인 분석

**4개 이상 파일**: 병렬 처리로 배치 추출
1. 캐시 디렉토리 생성
2. `jq`로 메시지 추출
3. 병렬 분석 작업 실행

**대용량 파일 (5000+ 토큰)**: 전처리 스크립트 사용

### Step 4: 결과 보고

발견사항 제시:
- 세션 요약
- 식별된 주요 패턴
- 주목할 만한 상호작용
- 추출된 인사이트

## Output Format

```markdown
## 세션 히스토리 분석

### 발견된 세션
- [세션 1]: [날짜] - [요약]
- [세션 2]: [날짜] - [요약]

### 식별된 패턴
- [패턴 1]
- [패턴 2]

### 주요 인사이트
- [인사이트 1]
- [인사이트 2]

### 권장사항
- [히스토리 패턴 기반]
```

## Constraints

- 출력 경로에 `~` 접두사 사용 (전체 경로 노출 금지)
- 배치 추출에 `jq` 필요
- 누락된 파일은 경고와 함께 우아하게 처리
