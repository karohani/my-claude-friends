---
name: session-analyzer
description: This skill should be used when the user asks to "analyze session", "세션 분석", "validate skill", "스킬 검증", "check session logs", "debug skill", "verify execution", or provides a session ID with a skill path to validate behavior against SKILL.md specifications.
version: 1.0.0
user-invocable: true
---

# Session Analyzer Skill

Post-hoc analysis of Claude Code sessions to validate behavior against SKILL.md specifications.

## Trigger

- `/session-analyzer`
- "세션 분석해줘"
- "validate session against skill"

## Purpose

Verify that skills, agents, and hooks behaved as specified in their SKILL.md definitions.

## Required Inputs

| Input | Description | Required |
|-------|-------------|----------|
| sessionId | UUID of session to analyze | Yes |
| targetSkill | Path to SKILL.md to validate against | Yes |
| additionalRequirements | Extra validation criteria | No |

## Workflow

### Step 1: Locate Session File

```bash
# Search in ~/.claude/ directory
find ~/.claude -name "*${sessionId}*" -type f
```

### Step 2: Parse SKILL.md

Extract expected components:
- Required tools
- Expected agents/subagents
- Hooks that should fire
- Artifacts to be created/modified

### Step 3: Analyze Debug Logs

Extract from session:
- SubAgent invocations
- Hook events fired
- Tool executions
- File operations

### Step 4: Verify Artifacts

Check file system:
- Were expected files created?
- Were files deleted as expected?
- Content validation where applicable

### Step 5: Compare and Report

Generate comparison table:

| Expected | Actual | Status |
|----------|--------|--------|
| [Component] | [What happened] | PASS/FAIL |

## Output Format

```markdown
## Session Analysis Report

### Summary
- Session ID: [UUID]
- Target Skill: [Path]
- Overall: PASS/FAIL

### Verification Details

| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Tool: Read | Called 3+ times | Called 5 times | PASS |
| Agent: doc-updater | Spawned | Spawned | PASS |
| Hook: PreToolUse | Fired | Not fired | FAIL |

### Issues Found
1. [Issue description]
   - Expected: [X]
   - Actual: [Y]
   - Impact: [Severity]

### Recommendations
- [How to fix identified issues]
```

## Use Cases

- Debugging skill behavior
- Validating new skill implementations
- Regression testing after changes
- Understanding session flow
