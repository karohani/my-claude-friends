# Onion Architecture

Detailed guide for structuring applications with a pure core and an imperative shell.

## Core Concept

The Onion Architecture (also called "Functional Core, Imperative Shell") organizes code into concentric layers:

```
┌─────────────────────────────────────────┐
│  Outer Shell: Actions (I/O, Effects)    │
│  ┌─────────────────────────────────┐    │
│  │  Middle: Orchestration          │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │  Core: Calculations     │    │    │
│  │  │  ┌─────────────────┐    │    │    │
│  │  │  │  Data            │    │    │    │
│  │  │  └─────────────────┘    │    │    │
│  │  └─────────────────────────┘    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

- **Core (innermost)**: Calculations and Data. Pure, deterministic, no dependencies on I/O.
- **Middle**: Orchestration logic that coordinates calculations and decides what actions to take.
- **Shell (outermost)**: Actions that interact with the outside world — database, network, file system, user interface.

## Dependency Direction

The critical rule: **dependencies point inward**. Inner layers know nothing about outer layers.

- Core does NOT import from Shell
- Core does NOT know about databases, HTTP, or file systems
- Shell depends on Core — it calls calculations and reads data
- Shell handles all I/O and passes results to Core

```typescript
// WRONG — Core depends on Shell (database)
function calculateDiscount(userId: string): number {
  const user = db.findUser(userId);  // Core reaches out to I/O!
  return user.isPremium ? 0.1 : 0;
}

// RIGHT — Core is pure, Shell passes data in
function calculateDiscount(isPremium: boolean): number {
  return isPremium ? 0.1 : 0;
}

// Shell handles I/O
async function applyDiscount(userId: string): Promise<number> {
  const user = await db.findUser(userId);         // Shell: I/O
  const discount = calculateDiscount(user.isPremium);  // Core: pure
  return discount;
}
```

## Implementation Pattern: Functional Core, Imperative Shell

### The Core (Calculations)

All business logic lives here. No imports of I/O libraries. Functions take data in, return data out.

```typescript
// core/pricing.ts — pure calculations
export function subtotal(items: LineItem[]): number {
  return items.reduce((sum, i) => sum + i.price * i.qty, 0);
}

export function applyDiscount(amount: number, discountRate: number): number {
  return amount * (1 - discountRate);
}

export function applyTax(amount: number, taxRate: number): number {
  return amount * (1 + taxRate);
}

export function orderSummary(
  items: LineItem[],
  discountRate: number,
  taxRate: number
): OrderSummary {
  const sub = subtotal(items);
  const discounted = applyDiscount(sub, discountRate);
  const total = applyTax(discounted, taxRate);
  return { subtotal: sub, discount: sub - discounted, tax: total - discounted, total };
}
```

### The Shell (Actions)

Thin layer that handles I/O and calls the core:

```typescript
// shell/orderHandler.ts — actions at the boundary
import { orderSummary } from "../core/pricing";

export async function handleCreateOrder(req: Request): Promise<Response> {
  // I/O: read
  const { items, userId, coupon } = await req.json();
  const user = await db.findUser(userId);
  const discountRate = await couponService.getRate(coupon);
  const taxRate = await taxService.getRateForRegion(user.region);

  // Core: pure calculation
  const summary = orderSummary(items, discountRate, taxRate);

  // I/O: write
  const order = await db.createOrder({ userId, ...summary, items });
  await emailService.sendConfirmation(user.email, order);

  return Response.json(order);
}
```

### The Pattern in Practice

```
Request → [Shell: parse & fetch data]
              ↓
         [Core: compute result]
              ↓
         [Shell: save & respond]
```

The shell is a thin sandwich: I/O → Pure → I/O.

## Directory Structure

Organize the codebase to reflect the architecture:

```
src/
├── core/                    # Pure calculations and data types
│   ├── pricing.ts
│   ├── validation.ts
│   ├── permissions.ts
│   └── types.ts
├── shell/                   # Actions, I/O, external interactions
│   ├── handlers/
│   │   ├── orderHandler.ts
│   │   └── userHandler.ts
│   ├── services/
│   │   ├── database.ts
│   │   └── email.ts
│   └── index.ts             # Entry point, wiring
└── shared/                  # Shared data types (no logic)
    └── types.ts
```

Rules:
- `core/` never imports from `shell/`
- `shell/` imports from `core/`
- `shared/` contains only type definitions (Data)

## Testing Benefits

### Core Tests — Fast, No Mocks

```typescript
describe("orderSummary", () => {
  it("calculates correctly with discount and tax", () => {
    const items = [{ price: 100, qty: 2 }];
    const result = orderSummary(items, 0.1, 0.08);
    expect(result.subtotal).toBe(200);
    expect(result.discount).toBe(20);
    expect(result.total).toBeCloseTo(194.4);
  });
});
```

No database setup. No mocking. No teardown. Instant execution.

### Shell Tests — Integration, Minimal Scope

```typescript
describe("handleCreateOrder", () => {
  it("orchestrates correctly", async () => {
    // Only mock I/O boundaries
    mockDb.findUser.mockResolvedValue({ region: "US" });
    mockCouponService.getRate.mockResolvedValue(0.1);
    // ... test the wiring, not the math
  });
});
```

Shell tests verify wiring — that the right data flows to the right calculation and the results get saved correctly. Business logic correctness is already proven by core tests.

## Relationship to Other Patterns

### Ports and Adapters (Hexagonal Architecture)

The Onion Architecture is closely related. "Ports" define interfaces at the boundary (what I/O the core needs). "Adapters" implement those interfaces (the actual database, email service, etc.).

```typescript
// Port — defined in core
interface OrderRepository {
  save(order: Order): Promise<void>;
}

// Adapter — implemented in shell
class PostgresOrderRepository implements OrderRepository {
  async save(order: Order): Promise<void> {
    await this.pool.query("INSERT INTO orders ...", [order]);
  }
}
```

### Event Sourcing

Store a sequence of events (Data) rather than current state. Reconstruct state by replaying events through calculations (reduce):

```typescript
// Events are Data
type CartEvent =
  | { type: "ITEM_ADDED"; item: Item }
  | { type: "ITEM_REMOVED"; itemId: string }
  | { type: "COUPON_APPLIED"; code: string };

// State reconstruction is a Calculation
function buildCart(events: CartEvent[]): Cart {
  return events.reduce((cart, event) => {
    switch (event.type) {
      case "ITEM_ADDED":
        return { ...cart, items: [...cart.items, event.item] };
      case "ITEM_REMOVED":
        return { ...cart, items: cart.items.filter(i => i.id !== event.itemId) };
      case "COUPON_APPLIED":
        return { ...cart, coupon: event.code };
    }
  }, emptyCart());
}
```

## Common Violations and Fixes

| Violation | Symptom | Fix |
|-----------|---------|-----|
| Core imports DB | `import { db } from "../database"` in a calculation file | Pass data as parameters instead |
| Logic in handler | 50+ line route handler with business rules | Extract calculations to core |
| God service | Service class with both I/O and business logic | Split into core calculations + shell service |
| Shared mutable state | Global variables accessed by core functions | Pass state as parameters, return new state |
| Test requires DB | Unit test needs database setup to test business logic | Extract the logic into a pure function |
