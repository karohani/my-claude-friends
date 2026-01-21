#!/usr/bin/env python3
"""
Recording script for voice-assistant plugin.

Uses sox to record audio from microphone.

Usage:
    python record.py [--duration SECONDS]

Output:
    Writes WAV file to configured path (default: /tmp/voice_input.wav)
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from config_loader import load_config, expand_path


def check_sox_installed() -> bool:
    """Check if sox is installed."""
    try:
        subprocess.run(
            ['sox', '--version'],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def record_audio(output_path: str, duration: int, sample_rate: int = 16000, channels: int = 1) -> bool:
    """
    Record audio using sox rec command.

    Args:
        output_path: Path to save the WAV file
        duration: Maximum recording duration in seconds
        sample_rate: Sample rate in Hz (default 16000 for Whisper)
        channels: Number of channels (default 1 for mono)

    Returns:
        True if recording was successful, False otherwise
    """
    if not check_sox_installed():
        print("Error: sox is not installed. Please run: brew install sox", file=sys.stderr)
        return False

    # Build sox rec command
    # rec -r 16000 -c 1 -b 16 output.wav trim 0 30
    cmd = [
        'rec',
        '-r', str(sample_rate),  # Sample rate
        '-c', str(channels),      # Channels
        '-b', '16',               # Bit depth
        output_path,
        'trim', '0', str(duration)  # Max duration
    ]

    print(f"Recording... Press Ctrl+C to stop (max {duration}s)")
    print("Speak now!")

    try:
        # Run recording
        result = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            print(f"\nRecording saved to: {output_path}")
            return True
        else:
            print(f"Recording failed: {result.stderr}", file=sys.stderr)
            return False

    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
        # Check if file was created
        if Path(output_path).exists():
            print(f"Recording saved to: {output_path}")
            return True
        return False


def main():
    parser = argparse.ArgumentParser(description="Record audio for voice input")
    parser.add_argument(
        '--duration', '-d',
        type=int,
        help='Maximum recording duration in seconds'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path'
    )

    args = parser.parse_args()

    # Load config
    config = load_config()
    recording_config = config.get('recording', {})

    # Get parameters (CLI args override config)
    duration = args.duration or recording_config.get('max_duration', 30)
    output_path = args.output or recording_config.get('output_path', '/tmp/voice_input.wav')
    output_path = expand_path(output_path)
    sample_rate = recording_config.get('sample_rate', 16000)
    channels = recording_config.get('channels', 1)

    # Record
    success = record_audio(output_path, duration, sample_rate, channels)

    # Print output path on success for piping to transcribe
    if success:
        print(output_path)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
