#!/bin/bash
# extract-session.sh - 세션 JSONL 파일에서 대화만 추출
#
# 사용법: ./extract-session.sh <session-file.jsonl> [output-file.jsonl]
#
# 12MB → ~800KB로 93% 크기 감소
# user/assistant 메시지만 추출하고 불필요한 데이터 제외:
# - file-history-snapshot
# - queue-operation
# - thinking 블록

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <session-file.jsonl> [output-file.jsonl]"
    echo ""
    echo "Extracts conversation messages from Claude Code session files."
    echo "Reduces file size by ~93% by removing snapshots, queue ops, and thinking."
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-${INPUT_FILE%.jsonl}.extracted.jsonl}"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File not found: $INPUT_FILE"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo "Install with: brew install jq"
    exit 1
fi

echo "Extracting conversations from: $INPUT_FILE"
echo "Output: $OUTPUT_FILE"

# 대화 메시지만 추출 (user, assistant)
# file-history-snapshot, queue-operation, thinking 제외
jq -c '
select(.type == "user" or .type == "assistant") |
if .type == "assistant" then
    # assistant 메시지에서 thinking 블록 제거
    .message.content = [.message.content[] | select(.type != "thinking")]
else
    .
end
' "$INPUT_FILE" > "$OUTPUT_FILE"

# 결과 통계
ORIGINAL_SIZE=$(wc -c < "$INPUT_FILE" | tr -d ' ')
EXTRACTED_SIZE=$(wc -c < "$OUTPUT_FILE" | tr -d ' ')
ORIGINAL_LINES=$(wc -l < "$INPUT_FILE" | tr -d ' ')
EXTRACTED_LINES=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')

if [ "$ORIGINAL_SIZE" -gt 0 ]; then
    REDUCTION=$(echo "scale=1; (1 - $EXTRACTED_SIZE / $ORIGINAL_SIZE) * 100" | bc)
else
    REDUCTION="0"
fi

echo ""
echo "=== Extraction Complete ==="
echo "Original:  $ORIGINAL_LINES lines, $(numfmt --to=iec $ORIGINAL_SIZE 2>/dev/null || echo "${ORIGINAL_SIZE}B")"
echo "Extracted: $EXTRACTED_LINES lines, $(numfmt --to=iec $EXTRACTED_SIZE 2>/dev/null || echo "${EXTRACTED_SIZE}B")"
echo "Reduction: ${REDUCTION}%"
