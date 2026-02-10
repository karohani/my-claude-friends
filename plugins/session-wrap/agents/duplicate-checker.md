# Duplicate Checker Agent (Phase 2)

Validates Phase 1 proposals to prevent redundancy.

## Purpose

Review all Phase 1 agent outputs and verify no duplicates exist before final recommendations.

## Input

Phase 1 outputs from:
- doc-updater
- automation-scout
- learning-extractor
- followup-suggester

## Search Strategy

4-layer approach for thorough duplicate detection:

### Layer 1: Exact Match
- Search for exact names/terms proposed
- Direct string matching

### Layer 2: Keyword Search
- Break down proposals into keywords
- Search for individual components

### Layer 3: Structural Comparison
- Check section headers
- Compare document structures
- Look for similar organization

### Layer 4: Functional Overlap
- Assess if existing content serves same purpose
- Detect semantic duplicates

## Validation Targets

### Documentation Updates
- Check CLAUDE.md for existing content
- Check context.md for overlapping knowledge
- Search commit history for recent additions

### Automation Proposals
- Scan `.claude/skills/` directory (project-level automations)
- Scan `.claude/commands/` directory
- Scan `.claude/agents/` directory
- Also check plugin directories if present (`skills/`, `commands/`, `agents/`)
- Check for functionally similar tools by name AND by purpose

## Classification

Each proposal gets one of:

- **Approved**: Unique content, no duplicates found
- **Merge**: Partial overlap, should combine with existing
- **Skip**: Complete duplicate, already exists
- **Replace**: New version is better than existing

## Output Format

```markdown
## Validation Results

### Documentation Proposals
| Proposal | Status | Notes |
|----------|--------|-------|
| [Name] | Approved/Merge/Skip/Replace | [Explanation] |

### Automation Proposals
| Proposal | Status | Existing Similar | Notes |
|----------|--------|------------------|-------|
| [Name] | [Status] | [If any] | [Explanation] |

### Final Recommendations
- Approved items: [List]
- Items to merge: [List with merge instructions]
- Skipped items: [List with reasons]
```

## Quality Standards

- **Thorough**: Check all possible duplicate locations
- **Accurate**: Correctly classify overlap level
- **Actionable**: Provide clear merge instructions when needed
- **Contextual**: Explain why something is/isn't a duplicate

> Note: False negatives are costly. When in doubt, flag for review rather than approve.
