# Higher-Order Functions

Detailed guide for first-class functions, higher-order patterns, and functional iteration.

## First-Class Functions

A first-class function can be stored in a variable, passed as an argument, and returned from another function — just like any other value.

```typescript
// Stored in a variable
const double = (x: number) => x * 2;

// Passed as an argument
[1, 2, 3].map(double);  // [2, 4, 6]

// Returned from a function
function multiplier(factor: number) {
  return (x: number) => x * factor;
}
const triple = multiplier(3);
triple(5);  // 15
```

## Refactoring Technique: Revealing Implicit Arguments

When function names contain implicit arguments, extract them into explicit parameters:

```typescript
// BAD — implicit argument in the name
function getShippingPrice(cart: Cart): number { ... }
function getTaxPrice(cart: Cart): number { ... }
function getDiscountPrice(cart: Cart): number { ... }

// GOOD — explicit argument as parameter
function getPrice(cart: Cart, priceType: PriceType): number { ... }
// Or even better, pass the calculation itself:
function applyPricing(cart: Cart, priceFn: (cart: Cart) => number): number {
  return priceFn(cart);
}
```

## Refactoring Technique: Replace Body with Callback

When multiple functions share the same structure but differ in a small section, extract the difference as a callback parameter:

```typescript
// BAD — duplicated structure
function logAndSaveUser(user: User): void {
  console.log("Processing...");
  try {
    db.saveUser(user);
    console.log("Done");
  } catch (e) {
    console.error("Failed", e);
  }
}

function logAndSaveOrder(order: Order): void {
  console.log("Processing...");
  try {
    db.saveOrder(order);
    console.log("Done");
  } catch (e) {
    console.error("Failed", e);
  }
}

// GOOD — extract the differing part as callback
function withLogging<T>(operation: () => T): T {
  console.log("Processing...");
  try {
    const result = operation();
    console.log("Done");
    return result;
  } catch (e) {
    console.error("Failed", e);
    throw e;
  }
}

withLogging(() => db.saveUser(user));
withLogging(() => db.saveOrder(order));
```

## Common Higher-Order Function Patterns

### Wrapper / Decorator

Wrap a function to add behavior without modifying it:

```typescript
// Retry wrapper
function withRetry<T>(fn: () => Promise<T>, maxAttempts: number): () => Promise<T> {
  return async () => {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (e) {
        if (attempt === maxAttempts) throw e;
      }
    }
    throw new Error("Unreachable");
  };
}

const fetchWithRetry = withRetry(() => fetch("/api/data"), 3);
```

### Memoization

Cache computation results for repeated calls:

```typescript
function memoize<T extends (...args: any[]) => any>(fn: T): T {
  const cache = new Map<string, ReturnType<T>>();
  return ((...args: Parameters<T>) => {
    const key = JSON.stringify(args);
    if (!cache.has(key)) cache.set(key, fn(...args));
    return cache.get(key)!;
  }) as T;
}

const expensiveCalc = memoize((n: number) => {
  // heavy computation
  return fibonacci(n);
});
```

### Partial Application

Fix some arguments to create a more specific function:

```typescript
function partial<T, A extends any[], R>(
  fn: (first: T, ...rest: A) => R,
  first: T
): (...rest: A) => R {
  return (...rest) => fn(first, ...rest);
}

const addTax = partial(multiply, 1.1);
addTax(100);  // 110
```

## Functional Iteration: map, filter, reduce

### map — Transform Each Element

Produce a new array of the same length by applying a function to each element:

```typescript
const prices = products.map(p => p.price);
const formatted = names.map(name => name.toUpperCase());

// Equivalent imperative loop (avoid this):
const prices: number[] = [];
for (const p of products) {
  prices.push(p.price);
}
```

**Use when**: Transforming each element into something else, one-to-one.

### filter — Select Elements

Produce a new array with only elements that pass a predicate:

```typescript
const active = users.filter(u => u.active);
const expensive = items.filter(i => i.price > 100);

// Multiple filters combine as AND
const result = users
  .filter(u => u.active)
  .filter(u => u.age >= 18);
```

**Use when**: Keeping elements that match a condition, removing those that do not.

### reduce — Aggregate to Single Value

Accumulate array elements into a single result:

```typescript
const total = items.reduce((sum, item) => sum + item.price, 0);

const grouped = items.reduce((groups, item) => {
  const key = item.category;
  return {
    ...groups,
    [key]: [...(groups[key] || []), item],
  };
}, {} as Record<string, Item[]>);
```

**Use when**: Combining all elements into one value (sum, product, object, string).

**Note**: `map` and `filter` can both be implemented using `reduce`, making `reduce` the most general of the three.

### Replacing Imperative Loops

| Loop Pattern | Functional Equivalent |
|-------------|----------------------|
| `for` + push results | `map` |
| `for` + conditional push | `filter` |
| `for` + accumulator | `reduce` |
| `for` + conditional + push | `filter` then `map` |
| `for` + find first match | `find` |
| `for` + check all/some | `every` / `some` |
| Nested `for` + flatten | `flatMap` |

### Example: Complex Loop → Functional Chain

```typescript
// BEFORE — imperative
const result: string[] = [];
for (const order of orders) {
  if (order.status === "completed") {
    for (const item of order.items) {
      if (item.price > 50) {
        result.push(item.name.toUpperCase());
      }
    }
  }
}

// AFTER — functional chain
const result = orders
  .filter(o => o.status === "completed")
  .flatMap(o => o.items)
  .filter(i => i.price > 50)
  .map(i => i.name.toUpperCase());
```

## Function Composition

### Pipe / Compose

Chain transformations in a readable pipeline:

```typescript
// Simple pipe implementation
function pipe<T>(...fns: Array<(arg: T) => T>): (arg: T) => T {
  return (arg) => fns.reduce((result, fn) => fn(result), arg);
}

const processUser = pipe(
  normalizeEmail,
  validateAge,
  assignDefaultRole,
);

const user = processUser(rawInput);
```

### Method Chaining vs Function Composition

```typescript
// Method chaining (built-in arrays)
const result = items
  .filter(i => i.active)
  .map(i => i.name)
  .sort();

// Function composition (custom functions)
const process = pipe(filterActive, extractNames, sortAlpha);
const result = process(items);
```

Both achieve the same goal. Method chaining works with built-in types. Function composition works with any functions.

## Stream Fusion Optimization

Sequential operations create intermediate arrays. Combine them when performance matters:

```typescript
// Two intermediate arrays created
const result = items
  .filter(i => i.active)   // intermediate array 1
  .map(i => i.name);       // intermediate array 2

// Single pass with reduce — one intermediate structure
const result = items.reduce<string[]>((acc, i) => {
  if (i.active) acc.push(i.name);
  return acc;
}, []);
```

Apply stream fusion only when profiling shows a bottleneck. Clarity is more important than micro-optimization in most cases.

## Utility Functions

Common helpers built with higher-order patterns:

```typescript
// pluck — extract a field from each object
const pluck = <T, K extends keyof T>(key: K) =>
  (items: T[]): T[K][] => items.map(item => item[key]);

const names = pluck("name")(users);

// groupBy — group items by a computed key
const groupBy = <T>(fn: (item: T) => string) =>
  (items: T[]): Record<string, T[]> =>
    items.reduce((groups, item) => {
      const key = fn(item);
      return { ...groups, [key]: [...(groups[key] || []), item] };
    }, {} as Record<string, T[]>);

const byCategory = groupBy((item: Product) => item.category)(products);
```
