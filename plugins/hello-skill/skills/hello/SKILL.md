---
name: hello
description: This skill should be used when the user asks to "hello", "hi", "안녕", "인사", "start session", "프로젝트 소개", "what can you do", or greets Claude at the beginning of a session. Provides a friendly greeting and summarizes current project status.
version: 1.0.0
user-invocable: true
---

# Hello Skill

첫 번째 예제 스킬 - Claude Code Skills 시스템 학습용

## Trigger

`/hello` 또는 사용자가 인사할 때

## Behavior

사용자에게 친근하게 인사하고 현재 프로젝트 상태를 간단히 요약한다.

## Steps

1. 사용자의 언어를 감지한다 (한국어/영어)
2. 해당 언어로 인사한다
3. 현재 작업 디렉토리의 프로젝트 구조를 간단히 파악한다
4. 오늘 할 수 있는 작업을 제안한다

## Output Format

```
[인사말]

현재 프로젝트: [프로젝트명]
주요 파일: [파일 목록]

제안: [오늘 할 수 있는 작업 1-2개]
```

## Notes

- 이 스킬은 Skills 시스템 학습을 위한 예제입니다
- SKILL.md 파일 구조와 작성법을 익히는 데 참고하세요
