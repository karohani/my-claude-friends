# Immutability Patterns

Detailed guide for maintaining immutability through Copy-on-Write and Defensive Copying.

## Why Immutability

Mutable data is an implicit output. When a function mutates its arguments or shared state, it creates hidden dependencies and unpredictable behavior. Immutable data transforms writes into reads — and reads are Calculations, not Actions.

## Copy-on-Write Pattern

The primary pattern for working with data inside trusted code. Three steps:

1. **Copy** the data structure
2. **Modify** the copy
3. **Return** the copy

### Arrays

```typescript
// BAD — mutates original
function addItem(items: string[], item: string): void {
  items.push(item);
}

// GOOD — Copy-on-Write
function addItem(items: string[], item: string): string[] {
  return [...items, item];
}
```

Common array operations:

| Mutating (avoid) | Immutable (prefer) |
|-------------------|-------------------|
| `arr.push(x)` | `[...arr, x]` |
| `arr.pop()` | `arr.slice(0, -1)` |
| `arr.unshift(x)` | `[x, ...arr]` |
| `arr.shift()` | `arr.slice(1)` |
| `arr.splice(i, 1)` | `arr.filter((_, idx) => idx !== i)` |
| `arr.sort()` | `[...arr].sort()` |
| `arr.reverse()` | `[...arr].reverse()` |
| `arr[i] = x` | `arr.map((v, idx) => idx === i ? x : v)` |

### Objects

```typescript
// BAD — mutates original
function setName(user: User, name: string): void {
  user.name = name;
}

// GOOD — Copy-on-Write
function setName(user: User, name: string): User {
  return { ...user, name };
}
```

Common object operations:

| Mutating (avoid) | Immutable (prefer) |
|-------------------|-------------------|
| `obj.key = value` | `{ ...obj, key: value }` |
| `delete obj.key` | `const { key, ...rest } = obj; return rest;` |
| `Object.assign(obj, other)` | `{ ...obj, ...other }` |

### Nested Structures

Each nesting level requires its own copy:

```typescript
interface Company {
  name: string;
  address: {
    city: string;
    zip: string;
  };
  employees: Employee[];
}

// BAD — only shallow copy, nested object still shared
function updateCity(company: Company, city: string): Company {
  const copy = { ...company };
  copy.address.city = city;  // mutates the shared nested object!
  return copy;
}

// GOOD — copy each level
function updateCity(company: Company, city: string): Company {
  return {
    ...company,
    address: { ...company.address, city },
  };
}
```

### Structural Sharing

Copy-on-Write naturally produces structural sharing. Only the changed path is copied; unchanged branches are shared references. This keeps memory usage efficient.

```
Original:     { a: 1, b: { c: 2, d: 3 }, e: [4, 5] }
After update:  { a: 1, b: { c: 9, d: 3 }, e: [4, 5] }
                 ↑ same    ↑ new copy     ↑ same reference
```

## Defensive Copying Pattern

Use Defensive Copying when data crosses a **trust boundary** — between your code and external/untrusted code (third-party libraries, API responses, user input, legacy modules).

### Two Rules

1. **Data entering safe zone**: Deep copy incoming data, discard the original reference
2. **Data leaving safe zone**: Send a deep copy out, keep the original safe

```typescript
// Data entering from untrusted API
function handleApiResponse(rawData: unknown): Order {
  const safeCopy = structuredClone(rawData);  // deep copy IN
  return validateAndParse(safeCopy);
}

// Data leaving to untrusted library
function sendToAnalytics(order: Order): void {
  const safeCopy = structuredClone(order);    // deep copy OUT
  analytics.track(safeCopy);  // library cannot mutate our order
}
```

### When to Use Which

| Situation | Pattern |
|-----------|---------|
| Internal data transformation | Copy-on-Write (shallow copy) |
| Receiving data from external API | Defensive Copying (deep copy) |
| Passing data to third-party library | Defensive Copying (deep copy) |
| Function parameters within your codebase | Copy-on-Write (shallow copy) |
| Data from `JSON.parse()` | Already a deep copy — safe |
| Data from user input / form | Defensive Copying (deep copy) |

### Deep Copy Methods

```typescript
// JavaScript/TypeScript
const copy = structuredClone(original);        // native, handles most types
const copy = JSON.parse(JSON.stringify(orig));  // simple but loses functions, dates, undefined

// With libraries
import { produce } from "immer";
const next = produce(original, draft => {
  draft.nested.value = 42;  // write naturally, Immer handles immutability
});
```

## Language-Specific Immutability Tools

### TypeScript

```typescript
// Use readonly for compile-time enforcement
interface User {
  readonly id: string;
  readonly name: string;
  readonly tags: readonly string[];
}

// ReadonlyArray prevents mutating methods
function process(items: ReadonlyArray<Item>): ReadonlyArray<Item> {
  return items.filter(i => i.active);  // OK — filter returns new array
  // items.push(x);  // Compile error!
}

// as const for literal types
const CONFIG = {
  maxRetries: 3,
  timeout: 5000,
} as const;
```

### Python

```python
# Use tuple instead of list
items = (1, 2, 3)          # immutable
# items.append(4)          # AttributeError

# Use frozenset instead of set
tags = frozenset({"a", "b"})

# Use dataclasses with frozen=True
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    id: str
    name: str
```

## Common Pitfalls

### Pitfall 1: Shallow Copy of Nested Data

```typescript
// WRONG — nested array is shared
const newUser = { ...user };
newUser.roles.push("admin");  // mutates original user.roles!

// RIGHT — copy the nested array too
const newUser = { ...user, roles: [...user.roles, "admin"] };
```

### Pitfall 2: Sort Mutates In Place

```typescript
// WRONG — sort mutates the original array
const sorted = items.sort((a, b) => a.price - b.price);

// RIGHT — copy first, then sort
const sorted = [...items].sort((a, b) => a.price - b.price);
// Or use toSorted (ES2023+)
const sorted = items.toSorted((a, b) => a.price - b.price);
```

### Pitfall 3: Array Destructuring Is Not Copying

```typescript
// WRONG — this just extracts, doesn't copy
const [first, ...rest] = items;
first.name = "changed";  // mutates the original object!

// RIGHT — deep copy if objects are nested
const [first, ...rest] = items.map(i => ({ ...i }));
```
