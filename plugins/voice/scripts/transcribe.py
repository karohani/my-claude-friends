#!/usr/bin/env python3
"""
STT (Speech-to-Text) script for voice-assistant plugin.

Supports two providers:
- whisper-cpp: Local transcription using whisper.cpp
- openai: OpenAI Whisper API

Usage:
    python transcribe.py [audio_file]
    python transcribe.py --provider openai audio.wav

Output:
    Prints transcribed text to stdout
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from config_loader import load_config, expand_path


def check_whisper_cpp_installed() -> bool:
    """Check if whisper-cpp (whisper) is installed."""
    try:
        result = subprocess.run(
            ['which', 'whisper'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def transcribe_with_whisper_cpp(audio_path: str, model_path: str) -> str:
    """
    Transcribe audio using whisper.cpp.

    Args:
        audio_path: Path to audio file (WAV)
        model_path: Path to whisper model file

    Returns:
        Transcribed text
    """
    if not check_whisper_cpp_installed():
        raise RuntimeError(
            "whisper-cpp is not installed. Please run:\n"
            "  brew install whisper-cpp"
        )

    model_path = expand_path(model_path)

    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Whisper model not found at: {model_path}\n"
            "Download with:\n"
            "  mkdir -p ~/.whisper\n"
            "  curl -L -o ~/.whisper/ggml-large-v3-turbo.bin \\\n"
            "    https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin"
        )

    # Create temp file for output
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        output_base = f.name[:-4]  # Remove .txt extension

    try:
        # Run whisper-cpp
        # whisper --model <model> --file <audio> --output-txt
        cmd = [
            'whisper',
            '--model', model_path,
            '--file', audio_path,
            '--output-file', output_base,
            '--output-txt',
            '--no-prints'  # Suppress progress output
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"whisper-cpp failed: {result.stderr}")

        # Read output file
        output_file = f"{output_base}.txt"
        if Path(output_file).exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            # Clean up
            Path(output_file).unlink()
            return text
        else:
            raise RuntimeError("whisper-cpp did not produce output file")

    finally:
        # Cleanup temp files
        for ext in ['.txt', '.srt', '.vtt']:
            temp_file = f"{output_base}{ext}"
            if Path(temp_file).exists():
                Path(temp_file).unlink()


def transcribe_with_openai(audio_path: str, model: str = "whisper-1") -> str:
    """
    Transcribe audio using OpenAI Whisper API.

    Args:
        audio_path: Path to audio file
        model: OpenAI model name (default: whisper-1)

    Returns:
        Transcribed text
    """
    try:
        import openai
    except ImportError:
        raise RuntimeError(
            "openai package not installed. Please run:\n"
            "  pip install openai"
        )

    client = openai.OpenAI()

    with open(audio_path, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            model=model,
            file=audio_file
        )

    return response.text


def transcribe(audio_path: str, provider: str = None, config: dict = None) -> str:
    """
    Transcribe audio file to text.

    Args:
        audio_path: Path to audio file
        provider: STT provider ('whisper-cpp' or 'openai')
        config: Configuration dict (optional, will load if not provided)

    Returns:
        Transcribed text
    """
    if config is None:
        config = load_config()

    stt_config = config.get('stt', {})
    provider = provider or stt_config.get('provider', 'whisper-cpp')

    if provider == 'whisper-cpp':
        model_path = stt_config.get('whisper_model', '~/.whisper/ggml-large-v3-turbo.bin')
        return transcribe_with_whisper_cpp(audio_path, model_path)
    elif provider == 'openai':
        model = stt_config.get('openai_model', 'whisper-1')
        return transcribe_with_openai(audio_path, model)
    else:
        raise ValueError(f"Unknown STT provider: {provider}")


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio to text")
    parser.add_argument(
        'audio_file',
        nargs='?',
        help='Path to audio file (default: from config)'
    )
    parser.add_argument(
        '--provider', '-p',
        choices=['whisper-cpp', 'openai'],
        help='STT provider (default: from config)'
    )

    args = parser.parse_args()

    # Load config
    config = load_config()

    # Get audio file path
    audio_path = args.audio_file
    if not audio_path:
        audio_path = config.get('recording', {}).get('output_path', '/tmp/voice_input.wav')
        audio_path = expand_path(audio_path)

    if not Path(audio_path).exists():
        print(f"Error: Audio file not found: {audio_path}", file=sys.stderr)
        print("Run record.py first to record audio.", file=sys.stderr)
        sys.exit(1)

    try:
        text = transcribe(audio_path, args.provider, config)
        print(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
