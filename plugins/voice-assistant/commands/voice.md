# Voice Assistant (/voice)

Voice input and output for Claude Code. Record voice, transcribe, and get spoken responses.

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

Read config from `${pluginDir}/config.json` and display status.

### /voice ask

1. **Record**: Run `uv run --directory ${pluginDir} python ${pluginDir}/scripts/record.py`
   - Inform user: "Recording... Press Ctrl+C when done (max 30s)"

2. **Transcribe**: Run `uv run --directory ${pluginDir} python ${pluginDir}/scripts/transcribe.py`
   - Display transcribed text

3. **Confirm**: Ask user if the transcription is correct
   - Options: "Yes, ask this", "Re-record", "Cancel"

4. **Process**: If confirmed, treat the transcribed text as user input

### /voice on|off

Edit `${pluginDir}/config.json`:
- Set `tts.enabled` to `true` or `false`

### /voice config

Read and display `${pluginDir}/config.json`

## Dependencies

- **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **sox**: `brew install sox`
- **whisper-cpp**: `brew install whisper-cpp`

Python dependencies are auto-installed via `uv run`.
