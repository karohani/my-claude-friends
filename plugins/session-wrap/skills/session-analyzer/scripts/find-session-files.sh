#!/bin/bash
# find-session-files.sh - 세션 ID로 관련 파일 찾기
#
# 사용법: ./find-session-files.sh <session-id>
#
# 검색 대상:
# - 메인 세션 로그 (.jsonl)
# - 디버그 로그 (.txt)
# - 에이전트 트랜스크립트
# - TODO 파일

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <session-id>"
    echo ""
    echo "Finds all files related to a Claude Code session."
    echo ""
    echo "Session ID can be:"
    echo "  - Full UUID: 0d2c9ac7-e0ab-427c-a9bc-709886b749c5"
    echo "  - Partial: 0d2c9ac7"
    echo ""
    echo "Files searched:"
    echo "  - ~/.claude/projects/*/     (session logs)"
    echo "  - ~/.claude/todos/          (todo files)"
    echo "  - ~/.claude/agent-transcripts/  (agent logs)"
    exit 1
fi

SESSION_ID="$1"
CLAUDE_DIR="${HOME}/.claude"

echo "=== Searching for Session: $SESSION_ID ==="
echo ""

# 메인 세션 로그
echo "--- Session Logs (.jsonl) ---"
find "$CLAUDE_DIR/projects" -name "*${SESSION_ID}*.jsonl" 2>/dev/null || echo "(none found)"
echo ""

# 디버그 로그
echo "--- Debug Logs ---"
if [ -d "$CLAUDE_DIR/logs" ]; then
    find "$CLAUDE_DIR/logs" -name "*${SESSION_ID}*" 2>/dev/null || echo "(none found)"
else
    echo "(logs directory not found)"
fi
echo ""

# TODO 파일
echo "--- TODO Files ---"
if [ -d "$CLAUDE_DIR/todos" ]; then
    find "$CLAUDE_DIR/todos" -name "*${SESSION_ID}*" 2>/dev/null || echo "(none found)"
else
    echo "(todos directory not found)"
fi
echo ""

# 에이전트 트랜스크립트
echo "--- Agent Transcripts ---"
if [ -d "$CLAUDE_DIR/agent-transcripts" ]; then
    find "$CLAUDE_DIR/agent-transcripts" -name "*${SESSION_ID}*" 2>/dev/null || echo "(none found)"
else
    echo "(agent-transcripts directory not found)"
fi
echo ""

# 최근 세션 파일 표시 (세션 ID 없이 호출 시 유용)
echo "=== Recent Session Files (last 5) ==="
find "$CLAUDE_DIR/projects" -name "*.jsonl" -type f 2>/dev/null | \
    xargs ls -lt 2>/dev/null | head -5 || echo "(none found)"

echo ""
echo "=== Session File Details ==="
SESSION_FILE=$(find "$CLAUDE_DIR/projects" -name "*${SESSION_ID}*.jsonl" 2>/dev/null | head -1)
if [ -n "$SESSION_FILE" ] && [ -f "$SESSION_FILE" ]; then
    echo "File: $SESSION_FILE"
    echo "Size: $(ls -lh "$SESSION_FILE" | awk '{print $5}')"
    echo "Lines: $(wc -l < "$SESSION_FILE")"
    echo "Modified: $(ls -l "$SESSION_FILE" | awk '{print $6, $7, $8}')"

    if command -v jq &> /dev/null; then
        echo ""
        echo "Message Types:"
        jq -r '.type' "$SESSION_FILE" 2>/dev/null | sort | uniq -c | sort -rn | head -10
    fi
else
    echo "(session file not found)"
fi
