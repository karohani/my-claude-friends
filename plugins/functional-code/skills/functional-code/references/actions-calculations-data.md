# Actions, Calculations, and Data

Detailed guide for classifying code and extracting calculations from actions.

## Classification Guide

### How to Identify Actions

A function is an Action if ANY of the following is true:

- **External reads**: Database queries, file reads, network requests, environment variables
- **External writes**: Database inserts/updates, file writes, HTTP responses, DOM manipulation, console output
- **Mutable state access**: Reading or writing global variables, shared state, closures over mutable variables
- **Non-determinism**: `Date.now()`, `Math.random()`, `crypto.randomUUID()`, system clock
- **Calling other Actions**: If a function calls an Action, it becomes an Action (contagious)

```typescript
// Action — reads DB (external read) and sends email (external write)
async function notifyUser(userId: string): Promise<void> {
  const user = await db.findUser(userId);   // external read
  await mailer.send(user.email, "Hello");   // external write
}

// Action — reads mutable global state
let counter = 0;
function increment(): number {
  return ++counter;  // reads and writes shared mutable state
}

// Action — non-deterministic
function generateId(): string {
  return `id-${Date.now()}-${Math.random()}`;
}
```

### How to Identify Calculations

A function is a Calculation if ALL of the following are true:

- Takes only explicit inputs (parameters)
- Returns only explicit outputs (return value)
- Same inputs always produce the same output
- No side effects whatsoever
- Does not call any Actions

```typescript
// Calculation — pure transformation
function fullName(first: string, last: string): string {
  return `${first} ${last}`;
}

// Calculation — deterministic aggregation
function totalPrice(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price * item.qty, 0);
}

// Calculation — validation
function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

### How to Identify Data

Data is any inert value. It cannot execute, has no behavior, and only has meaning when interpreted by code.

```typescript
// Data — plain object
const config = { maxRetries: 3, timeout: 5000 };

// Data — domain entity
interface User {
  id: string;
  name: string;
  email: string;
  active: boolean;
}

// Data — event record
const event = { type: "ORDER_PLACED", orderId: "123", timestamp: "2025-01-01T00:00:00Z" };
```

## Implicit vs Explicit I/O

### Implicit Inputs

Any way data enters a function besides its parameters:

```typescript
// BAD — implicit input (reads global)
let taxRate = 0.1;
function calculateTax(price: number): number {
  return price * taxRate;  // taxRate is an implicit input
}

// GOOD — explicit input (parameter)
function calculateTax(price: number, taxRate: number): number {
  return price * taxRate;
}
```

### Implicit Outputs

Any way a function affects the outside world besides its return value:

```typescript
// BAD — implicit output (mutates argument)
function addItem(cart: Item[], item: Item): void {
  cart.push(item);  // mutating the argument is an implicit output
}

// GOOD — explicit output (return value)
function addItem(cart: Item[], item: Item): Item[] {
  return [...cart, item];
}
```

### Common Implicit I/O Patterns

| Pattern | Type | Fix |
|---------|------|-----|
| Reading a global variable | Implicit input | Pass as parameter |
| Modifying a global variable | Implicit output | Return new value |
| Mutating function arguments | Implicit output | Return new copy |
| DOM manipulation | Implicit output | Return data, let caller update DOM |
| Console logging | Implicit output | Return data, let caller log |
| Reading `this` in a method | Implicit input | Pass as parameter or keep thin |

## Extraction Technique: Action → Calculation

The core refactoring pattern to improve code quality:

### Step-by-Step Process

1. **Identify the calculation** buried inside the action
2. **Extract** it into a new function
3. **Replace implicit inputs** with function parameters
4. **Replace implicit outputs** with return values
5. **Call** the new calculation from the original action

### Example: Before and After

```typescript
// BEFORE — everything is one Action
async function processCart(userId: string): Promise<void> {
  const user = await db.findUser(userId);
  const cart = await db.getCart(userId);

  let total = 0;
  for (const item of cart.items) {
    total += item.price * item.qty;
  }
  if (user.isPremium) {
    total *= 0.9;
  }
  const tax = total * 0.1;
  const finalTotal = total + tax;

  await db.saveOrder({ userId, total: finalTotal, items: cart.items });
  await emailService.sendReceipt(user.email, finalTotal);
}
```

```typescript
// AFTER — Calculations extracted, Action is thin

// Calculation: compute subtotal
function subtotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.qty, 0);
}

// Calculation: apply premium discount
function applyDiscount(amount: number, isPremium: boolean): number {
  return isPremium ? amount * 0.9 : amount;
}

// Calculation: compute tax
function withTax(amount: number, taxRate: number): number {
  return amount + amount * taxRate;
}

// Calculation: compose the total
function orderTotal(items: CartItem[], isPremium: boolean, taxRate: number): number {
  return withTax(applyDiscount(subtotal(items), isPremium), taxRate);
}

// Action: thin shell, only I/O
async function processCart(userId: string): Promise<void> {
  const user = await db.findUser(userId);
  const cart = await db.getCart(userId);
  const total = orderTotal(cart.items, user.isPremium, 0.1);
  await db.saveOrder({ userId, total, items: cart.items });
  await emailService.sendReceipt(user.email, total);
}
```

**What improved:**
- Four pure calculations are now independently testable
- The Action (`processCart`) is a thin orchestration shell
- Business rules (discount, tax) are explicit and reusable
- Each calculation can be verified without database or email setup

## Testing Strategy

### Testing Calculations

Calculations are trivial to test — no mocks, no setup, no teardown:

```typescript
describe("orderTotal", () => {
  it("sums items correctly", () => {
    const items = [{ price: 10, qty: 2 }, { price: 5, qty: 1 }];
    expect(subtotal(items)).toBe(25);
  });

  it("applies premium discount", () => {
    expect(applyDiscount(100, true)).toBe(90);
    expect(applyDiscount(100, false)).toBe(100);
  });

  it("adds tax", () => {
    expect(withTax(100, 0.1)).toBe(110);
  });
});
```

### Testing Actions

Actions need mocks/stubs but become simpler when calculations are extracted:

```typescript
describe("processCart", () => {
  it("orchestrates correctly", async () => {
    // Only need to verify I/O calls, not business logic
    mockDb.findUser.mockResolvedValue({ isPremium: true, email: "a@b.com" });
    mockDb.getCart.mockResolvedValue({ items: [{ price: 100, qty: 1 }] });
    await processCart("user-1");
    expect(mockDb.saveOrder).toHaveBeenCalledWith(
      expect.objectContaining({ total: 99 }) // 100 * 0.9 + 9 tax
    );
  });
});
```

## Signals That Extraction Is Needed

Watch for these code smells:

- A function that is hard to test without mocks → likely has mixed Action + Calculation
- A function with many parameters AND side effects → implicit I/O buried inside
- Business logic inside an event handler or route handler → extract calculations
- Duplicated logic across multiple Actions → shared Calculation waiting to be extracted
- Long functions → multiple calculations tangled with actions
