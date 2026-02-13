---
name: functional-code
description: This skill should be used when the user asks to "write functional code", "review code functionally", "functional programming", "함수형 프로그래밍", "함수형 코드 리뷰", "grokking simplicity", "separate effects", "pure functions", "순수 함수", "side effects", "부수효과", "immutable", "불변성", "action calculation data", "액션 계산 데이터", or wants to write or review code following functional programming principles that separate Actions, Calculations, and Data.
version: 1.0.0
user-invocable: true
---

# Functional Code

A skill for writing and reviewing code based on functional programming principles from "Grokking Simplicity" by Eric Normand. Classify every piece of code as an **Action**, **Calculation**, or **Data**, then structure the codebase so that effects are isolated, logic is pure, and data is immutable.

## Modes

This skill operates in two modes:

1. **Write Mode** — Guide new code to follow FP principles from the start.
2. **Review Mode** — Analyze existing code for FP violations and suggest improvements.

Determine the mode from user intent. If ambiguous, ask.

## Core Principles

All work in both modes is guided by these seven principles:

| # | Principle | Key Idea |
|---|-----------|----------|
| 1 | **Actions, Calculations, Data** | Classify every function; extract calculations from actions |
| 2 | **Minimize Implicit I/O** | Convert hidden inputs/outputs to explicit parameters and return values |
| 3 | **Immutability** | Never mutate; use Copy-on-Write internally, Defensive Copying at boundaries |
| 4 | **Stratified Design** | Organize functions into layers by abstraction level; call down, never up |
| 5 | **First-class Functions** | Replace duplicated patterns with higher-order functions |
| 6 | **Functional Iteration** | Prefer map/filter/reduce over imperative loops |
| 7 | **Onion Architecture** | Pure core (Calculations + Data) wrapped by an imperative shell (Actions) |

For detailed patterns and examples, consult the `references/` directory listed below.

## Three Categories of Code

Every piece of code falls into one of three categories:

**Action (Effect)** — Depends on when or how many times it runs. Includes I/O, network calls, database queries, logging, reading mutable state, and any operation with side effects.

**Calculation (Pure Function)** — Transforms inputs into outputs deterministically. Same input always produces same output. No side effects. Easy to test, compose, and reuse.

**Data (Inert Value)** — Plain values: objects, arrays, strings, numbers. Not executable. Represents facts.

```
Action:      sendEmail(to, body)        — effect, timing matters
Calculation: calculateTotal(items)      — pure, testable
Data:        { id: 1, name: "Alice" }   — inert fact
```

## Write Mode Workflow

When guiding the user to write new code:

### Step 1: Classify the Task

Identify which parts of the requirement are Actions, Calculations, or Data.

- **Actions**: File I/O, API calls, database operations, logging, user input
- **Calculations**: Validation, transformation, filtering, aggregation, business rules
- **Data**: Configuration objects, DTOs, domain entities, constants

### Step 2: Design Data First

Define the data structures. Data is the foundation — calculations operate on data, and actions move data in and out of the system.

### Step 3: Write Calculations

Write pure functions for all business logic. Each function takes explicit inputs and returns explicit outputs. No reading globals, no mutating arguments, no side effects.

```typescript
// Calculation — pure, testable
function applyDiscount(price: number, rate: number): number {
  return price * (1 - rate);
}

// Calculation — returns new data, no mutation
function addItem(cart: Item[], item: Item): Item[] {
  return [...cart, item];
}
```

### Step 4: Isolate Actions at Boundaries

Push all effects to the outer edges. Actions call calculations, never the reverse.

```typescript
// Action — at the boundary, calls calculations
async function processOrder(orderId: string): Promise<void> {
  const order = await db.findOrder(orderId);       // Action: read
  const total = calculateTotal(order.items);        // Calculation
  const receipt = formatReceipt(order, total);      // Calculation
  await emailService.send(order.email, receipt);    // Action: write
}
```

### Step 5: Enforce Immutability

Apply Copy-on-Write for all data transformations. Never mutate existing objects or arrays.

```typescript
// Bad — mutates original
function updateName(user: User, name: string): void {
  user.name = name;
}

// Good — Copy-on-Write
function updateName(user: User, name: string): User {
  return { ...user, name };
}
```

### Step 6: Leverage Higher-Order Functions

Replace imperative loops with map/filter/reduce. Extract common patterns into reusable higher-order functions.

```typescript
const activeNames = users
  .filter(u => u.active)
  .map(u => u.name);
```

## Review Mode Workflow

When reviewing existing code:

### Step 1: Read and Understand

Read the target code using the Read tool. Understand the overall structure before analyzing.

### Step 2: Classify Every Function

Label each function as Action or Calculation. List all side effects found:
- External reads (DB, file, network, globals, mutable state)
- External writes (DB, file, network, DOM, console, globals)
- Non-determinism (random, Date.now, environment)

### Step 3: Check Against Seven Principles

Run systematic checks:

1. **Action/Calculation Separation** — Are calculations mixed with actions? Can pure logic be extracted?
2. **Implicit I/O** — Are there hidden dependencies on globals, closures over mutable state, or unreturned mutations?
3. **Immutability** — Direct array/object mutations? Missing Copy-on-Write?
4. **Stratified Design** — Do high-level functions directly call low-level implementation details?
5. **First-class Functions** — Is there duplicated logic that differs only in a small callback?
6. **Functional Iteration** — Are there imperative loops replaceable with map/filter/reduce?
7. **Onion Architecture** — Is I/O interleaved with business logic instead of pushed to boundaries?

### Step 4: Generate Report

Present findings in this structure:

```
## Functional Code Review

### Summary
- Functions analyzed: N
- Actions: N | Calculations: N
- Issues found: N (by principle)

### Findings

#### [Principle Name] — Line X
**Issue**: [description]
**Current**: [code snippet]
**Suggested**: [improved code snippet]
**Why**: [explanation of the principle violated]
```

### Step 5: Suggest Next Steps

Ask the user whether to:
- Apply all suggested fixes
- Apply specific fixes
- Explain a specific principle in more detail

## Quick Reference

### Identifying Actions

A function is an Action if it does ANY of the following:
- Reads or writes to a database, file, or network
- Reads mutable global/shared state
- Modifies its arguments
- Calls console.log or any logging
- Uses Date.now(), Math.random(), or similar non-deterministic APIs
- Calls another Action

### Extraction Pattern (Action → Calculation)

1. Identify the calculation buried inside the action
2. Extract it into a new function with explicit parameters
3. Replace implicit inputs (globals) with function parameters
4. Replace implicit outputs (mutations) with return values
5. Call the new calculation from the original action

### Immutability Quick Rules

- Arrays: use spread `[...arr]`, `filter`, `map`, `slice` — never `push`, `pop`, `splice`, `sort` in place
- Objects: use spread `{...obj}` — never assign properties directly
- Nested: copy each level or use a library (e.g., Immer)
- Boundaries: use Defensive Copying (deep clone) when data crosses trust boundaries

## Additional Resources

### Reference Files

For detailed patterns, examples, and techniques, consult:

- **`references/actions-calculations-data.md`** — Detailed classification guide, extraction techniques, implicit I/O patterns
- **`references/immutability-patterns.md`** — Copy-on-Write, Defensive Copying, language-specific tools
- **`references/stratified-design.md`** — Layer organization, four design patterns, refactoring to layers
- **`references/higher-order-functions.md`** — First-class functions, HOF patterns, replacing loops, composition
- **`references/onion-architecture.md`** — Functional core / imperative shell, dependency direction, implementation patterns
