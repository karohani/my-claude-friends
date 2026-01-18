---
name: session-wrap
description: This skill should be used when the user asks to "wrap up", "wrap", "세션 마무리", "마무리해줘", "end session", "finish coding", "commit changes", "summarize session", or wants to conclude a coding session. Multi-agent analysis for documentation updates, automation opportunities, learnings, and follow-up tasks.
version: 1.0.0
user-invocable: true
---

# Session Wrap Skill

Comprehensive workflow for concluding coding sessions with multi-agent analysis.

## Trigger

- `/wrap` command
- "세션 마무리해줘"
- "wrap up this session"

## Allowed Tools

Bash(git:*), Read, Write, Edit, Glob, Grep, Task, AskUserQuestion

## Workflow

### Step 1: Git Status Check

```bash
git status --short
git diff --stat
```

Assess current changes before analysis.

### Step 2: Phase 1 - Parallel Analysis

Launch 4 agents **simultaneously** using Task tool:

| Agent | Model | Purpose |
|-------|-------|---------|
| doc-updater | sonnet | CLAUDE.md/context.md updates |
| automation-scout | sonnet | Automation opportunities |
| learning-extractor | sonnet | Lessons and discoveries |
| followup-suggester | sonnet | Next steps and priorities |

### Step 3: Phase 2 - Validation

After Phase 1 completes, run:

| Agent | Model | Purpose |
|-------|-------|---------|
| duplicate-checker | haiku | Validate proposals, prevent duplicates |

### Step 4: Result Integration

Synthesize all agent findings into comprehensive wrap analysis:

```markdown
## Session Wrap Analysis

### Documentation Updates
[From doc-updater, validated by duplicate-checker]

### Automation Opportunities
[From automation-scout, validated]

### Learnings
[From learning-extractor]

### Follow-up Tasks
[From followup-suggester]
```

### Step 5: User Action Selection

Present options using AskUserQuestion:

- **Create commit** (Recommended) - Commit current changes with generated message
- **Update CLAUDE.md** - Apply documentation proposals
- **Create automation** - Generate proposed skill/command/agent
- **Skip** - End without action

### Step 6: Execute Selected Actions

Perform user-selected operations.

## When to Use

- End of coding session
- Completing a feature
- Before context switch
- Project checkpoint

## When to Skip

- Trivial changes only
- Pure code reading session
- No meaningful work done
