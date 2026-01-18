#!/usr/bin/env python3
"""Configuration loader for voice-assistant plugin."""

import json
import os
from pathlib import Path
from typing import Any


def get_plugin_dir() -> Path:
    """Get the plugin directory path."""
    return Path(__file__).parent.parent


def load_config() -> dict[str, Any]:
    """Load configuration from config.json."""
    config_path = get_plugin_dir() / "config.json"

    if not config_path.exists():
        return get_default_config()

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_default_config() -> dict[str, Any]:
    """Return default configuration."""
    return {
        "stt": {
            "provider": "whisper-cpp",
            "whisper_model": "~/.whisper/ggml-large-v3-turbo.bin",
            "openai_model": "whisper-1"
        },
        "tts": {
            "enabled": True,
            "mode": "summary",
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


def expand_path(path: str) -> str:
    """Expand ~ and environment variables in path."""
    return os.path.expanduser(os.path.expandvars(path))


if __name__ == "__main__":
    # Test config loading
    config = load_config()
    print(json.dumps(config, indent=2))
