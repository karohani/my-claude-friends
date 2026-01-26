# Doc Updater Agent

Documentation analysis agent for session wrap-up.

## Purpose

Analyze session discoveries and determine what requires documentation updates.

## Target Files

- **CLAUDE.md**: Project-wide information (commands, skills, agents, environment setup)
- **context.md**: Project-specific knowledge (business context, constraints, tribal knowledge)
- **CHANGE_LOG.md**: Chronological change history (date + one-sentence summary)

## Analysis Steps

1. **Read current documentation** to establish baseline
2. **Identify candidates** using specific criteria for each file type
3. **Check for duplicates** via grep to prevent redundancy
4. **Format proposals** with exact content and rationale

## Documentation Criteria

### CLAUDE.md
- New tools or commands discovered
- Environment variables added
- Structural changes to project
- Workflow patterns affecting multiple areas

### context.md
- "Why" decisions were made
- Recurring issues and solutions
- Non-intuitive patterns
- Organizational memory not evident from code

### CHANGE_LOG.md
- Major tasks completed in the session
- Core changes based on git diff
- Date + verb-first one-sentence summary

## Output Format

```markdown
## Documentation Proposals

### CLAUDE.md Updates
- [ ] [Proposal 1]: [Exact content to add]
  - Rationale: [Why this should be documented]
  - Location: [Where in the file]

### context.md Updates
- [ ] [Proposal 1]: [Exact content to add]
  - Rationale: [Why this should be preserved]

### CHANGE_LOG.md Entry
- [ ] YYYY-MM-DD: [One-sentence summary]
  - Rationale: [Why this change is worth recording]
```

## Quality Standards

- Provide exact markdown text, not vague suggestions
- Include clear rationale for each proposal
- Specify precise file locations
- Verify no duplicates exist before proposing
