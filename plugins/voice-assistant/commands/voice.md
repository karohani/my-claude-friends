# Voice Assistant (/voice)

Voice input and output for Claude Code. Record voice, transcribe, and get spoken responses.

## Plugin Path

This plugin is located at: `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant`

## Allowed Tools

Bash, Read, Write, AskUserQuestion

## Usage

- `/voice` - Show voice assistant status and options
- `/voice ask` - Record voice and ask Claude (STT → Claude → TTS)
- `/voice on` - Enable TTS (speak responses)
- `/voice off` - Disable TTS
- `/voice config` - Show current configuration

## Workflow

### /voice

Read config from `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/config.json` and display status.

### /voice ask

1. **Record**: Run `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/.venv/bin/python /Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/scripts/record.py`
   - Inform user: "Recording... Press Ctrl+C when done (max 30s)"

2. **Transcribe**: Run `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/.venv/bin/python /Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/scripts/transcribe.py`
   - Display transcribed text

3. **Confirm**: Ask user if the transcription is correct
   - Options: "Yes, ask this", "Re-record", "Cancel"

4. **Process**: If confirmed, treat the transcribed text as user input

### /voice on|off

Edit `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/config.json`:
- Set `tts.enabled` to `true` or `false`

### /voice config

Read and display `/Users/jay/workspace/my-karohani-claude-code-plugin/plugins/voice-assistant/config.json`

## Dependencies

- **sox**: `brew install sox`
- **whisper-cpp**: `brew install whisper-cpp`
- **anthropic**: In plugin's .venv
