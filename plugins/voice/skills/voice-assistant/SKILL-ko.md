---
name: voice-assistant
description: This skill should be used when the user asks to "voice input", "음성 입력", "voice ask", "speak to me", "음성으로 말해줘", "read aloud", "TTS", "STT", "voice mode", "음성 모드", or wants to use voice input/output with Claude Code.
version: 1.0.0
user-invocable: true
---

# Voice Assistant Skill

Claude Code와의 상호작용을 위한 음성 입력(STT) 및 출력(TTS).

## Trigger

- `/voice` 커맨드
- "음성으로 질문할게"
- "voice input please"
- "speak the response"

## Allowed Tools

Bash, Read, Write, Edit, AskUserQuestion

## Features

### TTS (Text-to-Speech)

macOS `say` 명령을 사용하여 Claude의 응답을 자동으로 읽어준다:
- Claude Haiku로 응답 요약 (20-30단어)
- 언어 감지: 한국어 (Yuna) / 영어 (Samantha)
- 백그라운드 실행 (비차단)

### STT (Speech-to-Text)

음성을 녹음하고 텍스트로 전사:
- `sox`로 녹음 (16kHz, 모노, WAV)
- whisper.cpp (로컬) 또는 OpenAI API 지원

## Workflow

### Voice Ask (`/voice ask`)

1. **음성 녹음**
   ```bash
   uv run --directory ${pluginDir} python ${pluginDir}/scripts/record.py
   ```
   - Ctrl+C로 녹음 중지
   - 최대 녹음 시간: 30초

2. **전사**
   ```bash
   uv run --directory ${pluginDir} python ${pluginDir}/scripts/transcribe.py
   ```
   - 설정된 STT 제공자 사용

3. **전사 확인**
   - 전사된 텍스트 표시
   - 옵션: "네, 이걸로 질문", "다시 녹음", "취소"

4. **쿼리 처리**
   - 전사 내용을 사용자 입력으로 처리
   - TTS 훅이 응답을 읽어줌

### Toggle TTS (`/voice on|off`)

`${pluginDir}/config.json` 편집:
```json
{
  "tts": {
    "enabled": true  // 또는 false
  }
}
```

### Show Config (`/voice config`)

현재 설정 표시:
- STT 제공자 및 모델
- TTS 모드, 음성, 속도
- 녹음 설정

## Configuration

`config.json` 설정:

```json
{
  "stt": {
    "provider": "whisper-cpp",  // "whisper-cpp" 또는 "openai"
    "whisper_model": "~/.whisper/ggml-large-v3-turbo.bin",
    "openai_model": "whisper-1"
  },
  "tts": {
    "enabled": true,
    "mode": "summary",  // "summary" 또는 "full"
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

사용 전 설치:

```bash
# uv (Python 패키지 매니저)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 녹음
brew install sox

# STT (하나 선택)
brew install whisper-cpp  # 로컬
# 또는 OpenAI API 사용 (OPENAI_API_KEY 설정)

# Whisper 모델 (whisper-cpp용)
mkdir -p ~/.whisper
curl -L -o ~/.whisper/ggml-large-v3-turbo.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin
```

Python 의존성 (claude-agent-sdk)은 `uv run`으로 자동 설치된다.

## When to Use

- 핸즈프리 코딩 세션
- 접근성 필요 시
- 멀티태스킹 (다른 작업하며 듣기)
- 타이핑 없이 빠른 질문

## Technical Notes

- TTS는 Stop, Notification, PostToolUse(AskUserQuestion) 훅으로 실행
- STT는 수동 트리거 필요 (`/voice ask`)
- 오디오 형식: 16kHz, 모노, 16비트 WAV (Whisper 호환)
- Haiku 요약으로 TTS를 간결하고 빠르게 유지
