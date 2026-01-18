---
name: history-insight
description: This skill should be used when the user asks to "analyze history", "히스토리 분석", "session history", "세션 기록", "past sessions", "이전 세션", "capture insights", "find patterns", or wants to extract insights from Claude Code session history files.
version: 1.0.0
user-invocable: true
---

# History Insight Skill

Extract insights from Claude Code session history.

## Trigger

- `/history-insight`
- "세션 히스토리 분석해줘"
- "capture session history"
- "save session data"

## Purpose

Access and analyze Claude Code session history for review, summarization, or reference.

## Workflow

### Step 1: Determine Scope

Ask user:
- Current project only?
- All sessions?
- Specific date range?

### Step 2: Locate Session Files

Search for session files:

```bash
# Session files location
~/.claude/projects/

# Files are .jsonl format, encoded by directory path
```

### Step 3: Process Sessions

Adapt processing based on file count:

**1-3 files**: Load directly, analyze inline

**4+ files**: Batch extraction with parallel processing
1. Create cache directory
2. Extract messages via `jq`
3. Run parallel analysis tasks

**Large files (≥5000 tokens)**: Use preprocessing script

### Step 4: Report Results

Present findings:
- Session summaries
- Key patterns identified
- Notable interactions
- Extracted insights

## Output Format

```markdown
## Session History Analysis

### Sessions Found
- [Session 1]: [Date] - [Summary]
- [Session 2]: [Date] - [Summary]

### Patterns Identified
- [Pattern 1]
- [Pattern 2]

### Key Insights
- [Insight 1]
- [Insight 2]

### Recommendations
- [Based on history patterns]
```

## Constraints

- Use `~` prefix in output paths (no full paths)
- Requires `jq` for batch extraction
- Handle missing files gracefully with warnings
