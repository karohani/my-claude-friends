---
name: tdd
description: This skill should be used when the user asks to "tdd init", "setup tdd", "TDD 설정", "테스트 주도 개발 설정", "add tdd workflow", or wants to set up TDD for their project.
version: 1.0.0
user-invocable: true
---

# TDD Meta Plugin (/tdd)

Generate project-specific TDD workflow skills. Detects stack and creates customized `.claude/skills/tdd/SKILL.md` for each project.

## Trigger

`/tdd init`, "setup tdd", "add tdd workflow"

## Allowed Tools

Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion

## Usage

- `/tdd init` - Detect stack and generate project TDD skill
- `/tdd init --with-hooks` - Also generate auto-test hooks

## Workflow

### 1. Detect Project Stack

Run detection commands:
```bash
ls package.json pyproject.toml pytest.ini Cargo.toml go.mod Makefile pom.xml build.gradle 2>/dev/null
```

Identify primary stack:
- **Node.js**: package.json exists
  - Check for: jest, vitest, mocha in devDependencies
  - Detect: npm, yarn, pnpm from lock files
- **Python**: pyproject.toml, pytest.ini, or setup.py
  - Check for: pytest, unittest in dependencies
- **Go**: go.mod exists
- **Rust**: Cargo.toml exists
- **Java**: pom.xml or build.gradle exists

### 2. Ask User Preferences

```
Detected stack: [stack name]
Test framework: [detected or ask]

Options:
1. Test command: [default based on stack]
2. Test file pattern: [default pattern]
3. Include auto-test hooks? [yes/no]
```

### 3. Generate Project TDD Skill

Create `.claude/skills/tdd/SKILL.md` using template from `${pluginDir}/templates/[stack].md`

Variables to replace in template:
- `{{TEST_COMMAND}}` - e.g., `npm test`, `pytest`, `go test ./...`
- `{{TEST_PATTERN}}` - e.g., `**/*.test.ts`, `**/test_*.py`
- `{{FRAMEWORK}}` - e.g., `Jest`, `pytest`, `go test`

### 4. Generate Hooks (Optional)

If `--with-hooks` or user confirms, create `.claude/hooks.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "{{TEST_COMMAND}}", "timeout": 60 }]
      },
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "command": "{{TEST_COMMAND}}", "timeout": 60 }]
      }
    ]
  }
}
```

### 5. Confirm Setup

Display summary:
```
TDD Setup Complete!

Created files:
- .claude/skills/tdd/SKILL.md
- .claude/hooks.json (if requested)

Usage:
- /tdd           - Start TDD cycle
- /tdd red       - Write failing test
- /tdd green     - Make test pass
- /tdd refactor  - Improve code

Auto-test: [enabled/disabled]
```

## Templates Location

Templates are stored in `${pluginDir}/templates/`:
- `nodejs.md` - Node.js (Jest, Vitest, Mocha)
- `python.md` - Python (pytest, unittest)
- `go.md` - Go
- `rust.md` - Rust
- `generic.md` - Fallback template
