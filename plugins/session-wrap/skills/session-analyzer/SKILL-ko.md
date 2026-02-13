---
name: session-analyzer
description: This skill should be used when the user asks to "analyze session", "세션 분석", "validate skill", "스킬 검증", "check session logs", "debug skill", "verify execution", or provides a session ID with a skill path to validate behavior against SKILL.md specifications.
version: 1.0.0
user-invocable: true
---

# Session Analyzer Skill

Claude Code 세션의 사후 분석을 통해 SKILL.md 명세 대비 동작을 검증한다.

## Trigger

- `/session-analyzer`
- "세션 분석해줘"
- "validate session against skill"

## Purpose

스킬, 에이전트, 훅이 SKILL.md 정의에 명시된 대로 동작했는지 검증한다.

## Required Inputs

| 입력 | 설명 | 필수 |
|------|------|------|
| sessionId | 분석할 세션의 UUID | 예 |
| targetSkill | 검증 기준이 될 SKILL.md 경로 | 예 |
| additionalRequirements | 추가 검증 기준 | 아니오 |

## Workflow

### Step 1: 세션 파일 찾기

```bash
# ~/.claude/ 디렉토리에서 검색
find ~/.claude -name "*${sessionId}*" -type f
```

### Step 2: SKILL.md 파싱

기대되는 구성요소 추출:
- 필요한 도구
- 기대되는 에이전트/서브에이전트
- 실행되어야 할 훅
- 생성/수정될 아티팩트

### Step 3: 디버그 로그 분석

세션에서 추출:
- SubAgent 호출
- 실행된 훅 이벤트
- 도구 실행
- 파일 작업

### Step 4: 아티팩트 검증

파일 시스템 확인:
- 기대된 파일이 생성되었는가?
- 기대대로 파일이 삭제되었는가?
- 해당되는 경우 내용 검증

### Step 5: 비교 및 보고

비교 테이블 생성:

| 기대 | 실제 | 상태 |
|------|------|------|
| [구성요소] | [실제 결과] | PASS/FAIL |

## Output Format

```markdown
## 세션 분석 보고서

### 요약
- 세션 ID: [UUID]
- 대상 스킬: [경로]
- 전체 결과: PASS/FAIL

### 검증 상세

| 구성요소 | 기대 | 실제 | 상태 |
|---------|------|------|------|
| Tool: Read | 3회 이상 호출 | 5회 호출 | PASS |
| Agent: doc-updater | 생성됨 | 생성됨 | PASS |
| Hook: PreToolUse | 실행됨 | 미실행 | FAIL |

### 발견된 이슈
1. [이슈 설명]
   - 기대: [X]
   - 실제: [Y]
   - 영향: [심각도]

### 권장사항
- [식별된 이슈 해결 방법]
```

## Use Cases

- 스킬 동작 디버깅
- 새로운 스킬 구현 검증
- 변경 후 회귀 테스트
- 세션 흐름 이해
