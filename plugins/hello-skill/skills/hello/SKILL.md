---
name: hello
description: This skill should be used when the user asks to "hello", "hi", "안녕", "인사", "start session", "프로젝트 소개", "what can you do", or greets Claude at the beginning of a session. Provides a friendly greeting and summarizes current project status.
version: 1.0.0
user-invocable: true
---

# Hello Skill

A first example skill for learning the Claude Code Skills system.

## Trigger

`/hello` or when the user greets.

## Behavior

Greet the user in a friendly manner and provide a brief summary of the current project status.

## Steps

1. Detect the user's language (Korean/English)
2. Greet in the detected language
3. Briefly assess the project structure of the current working directory
4. Suggest tasks that can be done today

## Output Format

```
[Greeting]

Current project: [Project name]
Key files: [File list]

Suggestions: [1-2 tasks that can be done today]
```

## Notes

- This skill is an example for learning the Skills system
- Use it as a reference for SKILL.md file structure and writing conventions
