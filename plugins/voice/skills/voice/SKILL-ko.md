---
name: voice
description: This skill should be used when the user asks to "/voice", "/voice ask", "/voice on", "/voice off", "voice input", "음성 입력", "음성으로 질문", or wants to use voice commands.
version: 1.0.0
user-invocable: true
---

# Voice Command

voice-assistant의 별칭. 전체 문서는 `/voice-assistant:voice` 참조.

## Commands

- `/voice` 또는 `/voice config` - 설정 표시
- `/voice ask` - 음성 녹음, 전사, Claude에게 질문
- `/voice on` - TTS 활성화
- `/voice off` - TTS 비활성화

## Quick Actions

### /voice (기본)

`${pluginDir}/config.json`을 읽고 상태를 표시한다.

### /voice ask

1. 실행: `uv run --directory ${pluginDir} python ${pluginDir}/scripts/record.py`
2. 실행: `uv run --directory ${pluginDir} python ${pluginDir}/scripts/transcribe.py`
3. 사용자에게 확인 후 입력으로 처리

### /voice on

`${pluginDir}/config.json` 편집, `tts.enabled`를 `true`로 설정

### /voice off

`${pluginDir}/config.json` 편집, `tts.enabled`를 `false`로 설정
