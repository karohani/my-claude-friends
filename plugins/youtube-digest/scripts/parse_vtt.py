#!/usr/bin/env python3
"""
VTT 자막 파싱 스크립트

사용법:
    python parse_vtt.py <vtt_file> [--json] [--timestamps] [--no-dedup]

옵션:
    --json        JSON 형식으로 출력
    --timestamps  타임스탬프 포함
    --no-dedup    중복 제거 비활성화
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Caption:
    start: str
    end: str
    text: str


def parse_timestamp(ts: str) -> float:
    """타임스탬프를 초 단위로 변환"""
    parts = ts.replace(",", ".").split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(parts[0])


def format_timestamp(seconds: float) -> str:
    """초를 MM:SS 형식으로 변환"""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def parse_vtt(content: str) -> list[Caption]:
    """VTT 파일 내용을 파싱"""
    captions = []

    # WEBVTT 헤더 및 스타일 제거
    content = re.sub(r"^WEBVTT.*?\n\n", "", content, flags=re.DOTALL)
    content = re.sub(r"Kind:.*?\n", "", content)
    content = re.sub(r"Language:.*?\n", "", content)
    content = re.sub(r"STYLE\n.*?(?=\n\n)", "", content, flags=re.DOTALL)

    # 블록 분리
    blocks = re.split(r"\n\n+", content.strip())

    for block in blocks:
        lines = block.strip().split("\n")
        if not lines:
            continue

        # 타임스탬프 라인 찾기
        timestamp_line = None
        text_lines = []

        for line in lines:
            if "-->" in line:
                timestamp_line = line
            elif timestamp_line is not None:
                # HTML 태그 및 포지션 정보 제거
                clean_line = re.sub(r"<[^>]+>", "", line)
                clean_line = re.sub(r"&nbsp;", " ", clean_line)
                clean_line = clean_line.strip()
                if clean_line:
                    text_lines.append(clean_line)

        if timestamp_line and text_lines:
            # 타임스탬프 파싱
            match = re.search(r"(\d{1,2}:?\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{1,2}:?\d{2}:\d{2}[.,]\d{3})", timestamp_line)
            if match:
                captions.append(Caption(
                    start=match.group(1),
                    end=match.group(2),
                    text=" ".join(text_lines)
                ))

    return captions


def deduplicate_captions(captions: list[Caption]) -> list[Caption]:
    """중복 자막 제거 (자동 생성 자막용)"""
    if not captions:
        return []

    result = []
    prev_text = ""

    for caption in captions:
        # 이전 텍스트와 완전히 같거나 포함 관계면 스킵
        if caption.text == prev_text:
            continue
        if prev_text and caption.text.startswith(prev_text):
            # 이전 텍스트를 확장한 경우, 이전 것을 대체
            if result:
                result[-1] = caption
            else:
                result.append(caption)
        else:
            result.append(caption)
        prev_text = caption.text

    return result


def merge_short_captions(captions: list[Caption], min_duration: float = 2.0) -> list[Caption]:
    """짧은 자막들을 병합"""
    if not captions:
        return []

    result = []
    buffer_text = []
    buffer_start = None
    buffer_end = None

    for caption in captions:
        start_sec = parse_timestamp(caption.start)
        end_sec = parse_timestamp(caption.end)
        duration = end_sec - start_sec

        if buffer_start is None:
            buffer_start = caption.start
        buffer_end = caption.end
        buffer_text.append(caption.text)

        # 충분히 긴 자막이거나 버퍼가 꽉 찼으면 플러시
        total_duration = parse_timestamp(buffer_end) - parse_timestamp(buffer_start)
        if total_duration >= min_duration or len(buffer_text) >= 3:
            result.append(Caption(
                start=buffer_start,
                end=buffer_end,
                text=" ".join(buffer_text)
            ))
            buffer_text = []
            buffer_start = None
            buffer_end = None

    # 남은 버퍼 처리
    if buffer_text and buffer_start:
        result.append(Caption(
            start=buffer_start,
            end=buffer_end,
            text=" ".join(buffer_text)
        ))

    return result


def output_text(captions: list[Caption], with_timestamps: bool = False) -> str:
    """텍스트 형식으로 출력"""
    lines = []
    for caption in captions:
        if with_timestamps:
            ts = format_timestamp(parse_timestamp(caption.start))
            lines.append(f"[{ts}] {caption.text}")
        else:
            lines.append(caption.text)
    return "\n".join(lines)


def output_json(captions: list[Caption]) -> str:
    """JSON 형식으로 출력"""
    data = [
        {
            "start": caption.start,
            "end": caption.end,
            "start_seconds": parse_timestamp(caption.start),
            "text": caption.text
        }
        for caption in captions
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="VTT 자막 파싱")
    parser.add_argument("vtt_file", help="VTT 파일 경로")
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")
    parser.add_argument("--timestamps", action="store_true", help="타임스탬프 포함")
    parser.add_argument("--no-dedup", action="store_true", help="중복 제거 비활성화")
    parser.add_argument("--no-merge", action="store_true", help="짧은 자막 병합 비활성화")
    args = parser.parse_args()

    vtt_path = Path(args.vtt_file)
    if not vtt_path.exists():
        print(f"Error: 파일을 찾을 수 없습니다: {vtt_path}", file=sys.stderr)
        sys.exit(1)

    content = vtt_path.read_text(encoding="utf-8")
    captions = parse_vtt(content)

    if not args.no_dedup:
        captions = deduplicate_captions(captions)

    if not args.no_merge:
        captions = merge_short_captions(captions)

    if args.json:
        print(output_json(captions))
    else:
        print(output_text(captions, with_timestamps=args.timestamps))


if __name__ == "__main__":
    main()
