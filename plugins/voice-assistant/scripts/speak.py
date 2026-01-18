#!/usr/bin/env python3
"""
TTS script for voice-assistant plugin.

Receives Claude's response, summarizes with Haiku, and speaks using macOS say.

Usage (from Stop hook):
    Environment variables:
    - CLAUDE_STOP_RESPONSE: Claude's response text (JSON)
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from config_loader import load_config


def detect_language(text: str) -> str:
    """Detect if text is primarily Korean or English."""
    korean_chars = len(re.findall(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]', text))
    total_chars = len(re.findall(r'\w', text))

    if total_chars == 0:
        return "en"

    korean_ratio = korean_chars / total_chars
    return "ko" if korean_ratio > 0.3 else "en"


def summarize_with_haiku(text: str, max_words: int = 10) -> str:
    """Use Claude Haiku to summarize text to a short phrase."""
    try:
        import anthropic

        client = anthropic.Anthropic()

        # Detect language for prompt
        lang = detect_language(text)
        if lang == "ko":
            prompt = f"다음 텍스트를 3~10단어로 핵심만 요약해줘. 요약만 출력해:\n\n{text[:2000]}"
        else:
            prompt = f"Summarize this text in 3-10 words. Output only the summary:\n\n{text[:2000]}"

        response = client.messages.create(
            model="claude-haiku-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        summary = response.content[0].text.strip()
        # Remove quotes if present
        summary = summary.strip('"\'')
        return summary

    except Exception as e:
        # Fallback: return first sentence or truncated text
        first_sentence = text.split('.')[0].split('。')[0][:100]
        return first_sentence if first_sentence else text[:50]


def speak(text: str, voice: str, rate: int = 190) -> None:
    """Speak text using macOS say command (background)."""
    # Escape special characters for shell
    escaped_text = text.replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')

    cmd = ['say', '-v', voice, '-r', str(rate), escaped_text]

    # Run in background so it doesn't block Claude
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )


def extract_response_text(stop_response: str) -> str:
    """Extract plain text from Claude's stop response."""
    try:
        data = json.loads(stop_response)
        # Handle different response formats
        if isinstance(data, dict):
            if 'response' in data:
                return data['response']
            if 'content' in data:
                content = data['content']
                if isinstance(content, list):
                    # Extract text from content blocks
                    texts = []
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            texts.append(block.get('text', ''))
                        elif isinstance(block, str):
                            texts.append(block)
                    return ' '.join(texts)
                return str(content)
        return str(data)
    except json.JSONDecodeError:
        return stop_response


def main():
    config = load_config()
    tts_config = config.get('tts', {})

    # Check if TTS is enabled
    if not tts_config.get('enabled', True):
        return

    # Get Claude's response from environment
    stop_response = os.environ.get('CLAUDE_STOP_RESPONSE', '')

    if not stop_response:
        return

    # Extract text from response
    response_text = extract_response_text(stop_response)

    if not response_text or len(response_text.strip()) < 5:
        return

    # Get mode (summary or full)
    mode = tts_config.get('mode', 'summary')

    if mode == 'summary':
        text_to_speak = summarize_with_haiku(response_text)
    else:
        # Full mode: limit to first 500 chars
        text_to_speak = response_text[:500]

    # Detect language and select voice
    lang = detect_language(text_to_speak)
    if lang == 'ko':
        voice = tts_config.get('voice_ko', 'Yuna')
    else:
        voice = tts_config.get('voice_en', 'Samantha')

    rate = tts_config.get('rate', 190)

    # Speak!
    speak(text_to_speak, voice, rate)


if __name__ == "__main__":
    main()
