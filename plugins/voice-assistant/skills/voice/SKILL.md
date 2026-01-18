---
name: voice
description: This skill should be used when the user asks to "/voice", "/voice ask", "/voice on", "/voice off", "voice input", "음성 입력", "음성으로 질문", or wants to use voice commands.
version: 1.0.0
user-invocable: true
---

# Voice Command

Alias for voice-assistant. See `/voice-assistant:voice` for full documentation.

## Plugin Path

`/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant`

## Commands

- `/voice` or `/voice config` - Show configuration
- `/voice ask` - Record voice, transcribe, ask Claude
- `/voice on` - Enable TTS
- `/voice off` - Disable TTS

## Quick Actions

### /voice (default)

Read `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/config.json` and show status.

### /voice ask

1. Run: `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/.venv/bin/python /Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/scripts/record.py`
2. Run: `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/.venv/bin/python /Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/scripts/transcribe.py`
3. Confirm with user, then process as input

### /voice on

Edit `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/config.json`, set `tts.enabled` to `true`

### /voice off

Edit `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/config.json`, set `tts.enabled` to `false`
