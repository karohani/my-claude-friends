# TDD (/tdd)

Meta plugin for generating project-specific TDD workflows.

## Allowed Tools

Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion

## Usage

- `/tdd init` - Detect stack and generate project TDD skill
- `/tdd init --with-hooks` - Also generate auto-test hooks

## What It Does

1. Detects project stack (Node.js, Python, Go, etc.)
2. Creates `.claude/skills/tdd/SKILL.md` customized for your project
3. Optionally creates `.claude/hooks.json` for auto-testing

## Reference

See `skills/tdd/SKILL.md` for detailed workflow.
