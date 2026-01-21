#!/usr/bin/env python3
"""
TTS hook: Summarizes and speaks the last Claude response.

Based on say-summary plugin from team-attention.

- Extracts the last assistant message from transcript
- Uses Claude Agent SDK (Haiku) to summarize in 20-30 words
- Speaks the summary via macOS say command
- Runs in background so hook exits immediately
- Triggered by: Stop, Notification, PostToolUse(AskUserQuestion)
"""

import asyncio
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from config_loader import load_config

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, TextBlock,
                              query)

LOG_FILE = Path("/tmp/voice-assistant-hook.log")


def log(message: str) -> None:
    """Write message to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def get_latest_transcript() -> Path | None:
    """Find the most recently modified transcript file across all projects.

    Since hooks run from plugin cache directory (not project directory),
    we search all project directories for the latest transcript.
    """
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.is_dir():
        return None

    # Find all transcript files across all projects
    all_transcripts = list(projects_dir.glob("*/*.jsonl"))
    if not all_transcripts:
        return None

    # Return the most recently modified one
    return max(all_transcripts, key=lambda f: f.stat().st_mtime)


def extract_last_assistant_message(transcript_path: Path) -> str | None:
    """Extract last assistant message from transcript."""
    try:
        with open(transcript_path, "r") as f:
            lines = f.readlines()

        # Search in reverse order
        for line in reversed(lines):
            try:
                data = json.loads(line)
                message = data.get("message", {})

                if message and message.get("role") == "assistant":
                    content = message.get("content", [])

                    # Extract text type items
                    text_parts = [
                        item.get("text", "")
                        for item in content
                        if isinstance(item, dict) and item.get("type") == "text"
                    ]

                    full_text = "".join(text_parts)
                    if full_text:
                        return full_text

            except json.JSONDecodeError:
                continue

    except Exception as e:
        log(f"Error reading transcript: {e}")

    return None


async def summarize_with_haiku(text: str) -> str:
    """Summarize message to 30 words or less using Claude Haiku."""
    # Return as-is if already 30 words or less
    if len(text.split()) <= 30:
        return text.strip()

    # Truncate for faster processing
    truncated = text[:1000] if len(text) > 1000 else text

    system_prompt = "You are a summarizer. Output ONLY a 20-30 word summary. No questions. No commentary. No offers to help. Just the summary. If the text contains both English and Korean, write the summary in Korean."

    options = ClaudeAgentOptions(
        model="haiku",
        system_prompt=system_prompt,
        allowed_tools=[],
        max_turns=1
    )

    response_text = ""
    try:
        async for message in query(prompt=f"요약할 텍스트: {truncated}", options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
        # Return after consuming all messages
        return response_text.strip() if response_text else text[:50].strip()
    except Exception as e:
        log(f"Haiku summarization failed: {e}")
        return text[:50].strip()


def detect_korean(text: str) -> bool:
    """Check if text contains Korean characters."""
    for char in text:
        if '\uac00' <= char <= '\ud7a3':  # 한글 음절
            return True
        if '\u1100' <= char <= '\u11ff':  # 한글 자모
            return True
    return False


def speak(text: str, config: dict) -> None:
    """Speak text via macOS say command (background).

    - Uses rate from config for natural pace
    - Detects language: Korean uses voice_ko, English uses voice_en
    """
    tts_config = config.get('tts', {})
    rate = tts_config.get('rate', 190)
    voice_ko = tts_config.get('voice_ko', 'Yuna')
    voice_en = tts_config.get('voice_en', 'Samantha')

    cmd = ["nohup", "say", "-r", str(rate)]

    if detect_korean(text):
        cmd.extend(["-v", voice_ko])
    else:
        cmd.extend(["-v", voice_en])

    cmd.append(text)

    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )


async def async_main() -> None:
    log("=== HOOK START ===")

    # Load config
    config = load_config()
    tts_config = config.get('tts', {})

    # Check if TTS is enabled
    if not tts_config.get('enabled', True):
        log("TTS disabled in config")
        return

    # 1. Find latest transcript file (across all projects)
    transcript_path = get_latest_transcript()
    if not transcript_path:
        log("No transcript file found")
        return
    log(f"Transcript: {transcript_path}")

    # 2. Extract last assistant message
    last_message = extract_last_assistant_message(transcript_path)
    if not last_message:
        log("No assistant message found")
        return
    log(f"Found message ({len(last_message)} chars)")

    # 3. Summarize with Haiku (if mode is summary)
    mode = tts_config.get('mode', 'summary')
    if mode == 'summary':
        summary = await summarize_with_haiku(last_message)
    else:
        # Full mode: limit to first 500 chars
        summary = last_message[:500]
    log(f"Summary: {summary}")

    # 4. Speak summary
    speak(summary, config)

    log("=== HOOK END ===")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
