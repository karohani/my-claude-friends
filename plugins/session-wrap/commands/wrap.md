# Session Wrap-up (/wrap)

Session wrap-up - analyze session, suggest documentation updates, automation opportunities, and follow-up tasks.

## Allowed Tools

Bash(git:*), Read, Write, Edit, Glob, Grep, Task, AskUserQuestion

## Usage

- `/wrap` - Interactive session wrap-up (recommended)
- `/wrap [message]` - Quick commit with provided message

## Workflow

Execute the session-wrap skill workflow:

1. **Git Status Check**: Run `git status --short` and `git diff --stat`

2. **Phase 1 - Parallel Analysis**: Launch 4 agents simultaneously
   - doc-updater agent
   - automation-scout agent
   - learning-extractor agent
   - followup-suggester agent

3. **Phase 2 - Validation**: Run duplicate-checker agent on Phase 1 results

4. **Integration**: Synthesize all findings into wrap analysis

5. **User Selection**: Present action options
   - Create commit (Recommended)
   - Update CLAUDE.md
   - Create automation
   - Skip

6. **Execute**: Perform selected actions

## Reference

See `skills/session-wrap/SKILL.md` for detailed workflow specification.
