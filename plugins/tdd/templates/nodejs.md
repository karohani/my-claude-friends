# TDD Workflow (/tdd)

Test-Driven Development workflow for this project.

**Stack**: Node.js
**Framework**: {{FRAMEWORK}}
**Test Command**: `{{TEST_COMMAND}}`

## Trigger

This skill should be used when the user asks to "tdd", "test first", "write test", "red green refactor", "테스트 먼저", "TDD", or wants to follow TDD methodology.

## Allowed Tools

Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion

## Usage

- `/tdd` - Show current phase and guidance
- `/tdd red` - Start RED phase (write failing test)
- `/tdd green` - Start GREEN phase (make test pass)
- `/tdd refactor` - Start REFACTOR phase
- `/tdd run` - Run tests

## Test Command

```bash
{{TEST_COMMAND}}
```

## Test File Pattern

`{{TEST_PATTERN}}`

## TDD Cycle

### RED Phase - Write Failing Test

1. Create test file matching pattern: `{{TEST_PATTERN}}`
2. Write a test that describes expected behavior
3. Run tests - they MUST fail
4. Confirm failure message makes sense

```bash
# Run tests - expect RED
{{TEST_COMMAND}}
```

**Test Template**:
```typescript
describe('FeatureName', () => {
  it('should do something specific', () => {
    // Arrange
    const input = ...;

    // Act
    const result = functionUnderTest(input);

    // Assert
    expect(result).toBe(expected);
  });
});
```

### GREEN Phase - Make Test Pass

1. Write the MINIMUM code to pass the test
2. No extra features, no optimization
3. It's okay if the code is ugly

```bash
# Run tests - expect GREEN
{{TEST_COMMAND}}
```

**Principle**: Write just enough code. Resist the urge to add more.

### REFACTOR Phase

1. Improve code quality while tests stay green
2. One small change at a time
3. Run tests after EACH change

Checklist:
- [ ] Remove duplication
- [ ] Improve naming
- [ ] Extract functions if too long
- [ ] Simplify conditionals

```bash
# Run tests after each refactor
{{TEST_COMMAND}}
```

## Best Practices

1. **One test at a time** - Don't write multiple failing tests
2. **Small steps** - Each cycle should take < 5 minutes
3. **Commit often** - Commit after each GREEN phase
4. **Test behavior, not implementation** - Tests should survive refactoring
