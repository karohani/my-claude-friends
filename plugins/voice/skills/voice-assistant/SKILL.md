---
name: voice-assistant
description: This skill should be used when the user asks to "voice input", "음성 입력", "voice ask", "speak to me", "음성으로 말해줘", "read aloud", "TTS", "STT", "voice mode", "음성 모드", or wants to use voice input/output with Claude Code.
version: 1.0.0
user-invocable: true
---

# Voice Assistant Skill

Voice input (STT) and output (TTS) for Claude Code interactions.

## Trigger

- `/voice` command
- "음성으로 질문할게"
- "voice input please"
- "speak the response"

## Allowed Tools

Bash, Read, Write, Edit, AskUserQuestion

## Features

### TTS (Text-to-Speech)

Automatically speaks Claude's responses using macOS `say` command:
- Uses Claude Haiku to summarize responses (20-30 words)
- Language detection: Korean (Yuna) / English (Samantha)
- Runs in background (non-blocking)

### STT (Speech-to-Text)

Records voice and transcribes to text:
- Uses `sox` for recording (16kHz, mono, WAV)
- Supports whisper.cpp (local) or OpenAI API

## Workflow

### Voice Ask (`/voice ask`)

1. **Record Voice**
   ```bash
   uv run --directory ${pluginDir} python ${pluginDir}/scripts/record.py
   ```
   - Press Ctrl+C to stop recording
   - Max duration: 30 seconds

2. **Transcribe**
   ```bash
   uv run --directory ${pluginDir} python ${pluginDir}/scripts/transcribe.py
   ```
   - Uses configured STT provider

3. **Confirm Transcription**
   - Show transcribed text
   - Options: "Yes, ask this", "Re-record", "Cancel"

4. **Process Query**
   - Treat transcription as user input
   - TTS hook speaks response

### Toggle TTS (`/voice on|off`)

Edit `${pluginDir}/config.json`:
```json
{
  "tts": {
    "enabled": true  // or false
  }
}
```

### Show Config (`/voice config`)

Display current settings:
- STT provider and model
- TTS mode, voices, rate
- Recording settings

## Configuration

`config.json` settings:

```json
{
  "stt": {
    "provider": "whisper-cpp",  // "whisper-cpp" or "openai"
    "whisper_model": "~/.whisper/ggml-large-v3-turbo.bin",
    "openai_model": "whisper-1"
  },
  "tts": {
    "enabled": true,
    "mode": "summary",  // "summary" or "full"
    "voice_ko": "Yuna",
    "voice_en": "Samantha",
    "rate": 190
  },
  "recording": {
    "sample_rate": 16000,
    "channels": 1,
    "max_duration": 30,
    "output_path": "/tmp/voice_input.wav"
  }
}
```

## Dependencies

Install before using:

```bash
# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Recording
brew install sox

# STT (choose one)
brew install whisper-cpp  # Local
# OR use OpenAI API (set OPENAI_API_KEY)

# Whisper model (for whisper-cpp)
mkdir -p ~/.whisper
curl -L -o ~/.whisper/ggml-large-v3-turbo.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin
```

Python dependencies (claude-agent-sdk) are auto-installed via `uv run`.

## When to Use

- Hands-free coding sessions
- Accessibility needs
- Multi-tasking (listening while doing other work)
- Quick questions without typing

## Technical Notes

- TTS runs via Stop, Notification, and PostToolUse(AskUserQuestion) hooks
- STT requires manual trigger (`/voice ask`)
- Audio format: 16kHz, mono, 16-bit WAV (Whisper-compatible)
- Haiku summarization keeps TTS concise and fast
