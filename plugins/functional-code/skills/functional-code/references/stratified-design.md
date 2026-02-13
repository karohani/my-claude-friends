# Stratified Design

Detailed guide for organizing code into layers by abstraction level.

## Core Concept

Stratified Design organizes functions into horizontal layers. Each layer is built on top of the layers beneath it. Functions in a given layer call functions from the same or lower layers — never from higher layers.

```
Layer 5: Application / I/O shell         (Actions — least reusable, changes often)
Layer 4: Business workflows               (Actions calling calculations)
Layer 3: Business rules / domain logic     (Calculations — core value)
Layer 2: Generic utilities / data ops      (Calculations — reusable)
Layer 1: Language built-ins / primitives   (Provided by runtime)
```

## Four Design Patterns

### Pattern 1: Straightforward Implementations

The function body should solve the problem at the right level of detail for its signature. If a function's name suggests a high-level operation, its body should read like a high-level description — not low-level manipulation.

```typescript
// BAD — high-level name, low-level body
function placeOrder(cart: Cart, user: User): Order {
  let total = 0;
  for (const item of cart.items) {
    total += item.price * item.qty;
    if (item.taxable) total += item.price * item.qty * 0.1;
  }
  if (user.isPremium) total *= 0.9;
  const orderId = `ORD-${Date.now()}`;
  // ... 30 more lines of detail
}

// GOOD — body matches the abstraction level of the name
function placeOrder(cart: Cart, user: User): Order {
  const subtotal = calculateSubtotal(cart.items);
  const total = applyPricingRules(subtotal, user);
  return createOrder(cart, user, total);
}
```

### Pattern 2: Abstraction Barriers

A layer that hides implementation details so that code above does not need to know how things work below. Changes below the barrier do not ripple upward.

```typescript
// Abstraction barrier: "cart operations"
// Callers above don't know if cart is an array, map, or database
function addToCart(cart: Cart, item: Item): Cart { ... }
function removeFromCart(cart: Cart, itemId: string): Cart { ... }
function cartTotal(cart: Cart): number { ... }

// Code above the barrier uses these functions freely
// without knowing the internal cart structure
function checkout(cart: Cart, user: User): Order {
  const total = cartTotal(cart);
  return createOrder(user, total);
}
```

### Pattern 3: Minimal Interface

Keep the public surface area of each layer small. Define only the operations necessary for the layer above to accomplish its work. Additional operations should be composed from existing ones, not added to the interface.

```typescript
// Minimal interface for a set of user operations
function createUser(data: UserInput): User { ... }
function updateUser(user: User, changes: Partial<User>): User { ... }
function deactivateUser(user: User): User {
  return updateUser(user, { active: false });  // composed from existing
}
```

### Pattern 4: Comfortable Layers

Be pragmatic. Not every piece of code needs perfect stratification. Add layers when they make the code easier to understand, test, or change. Stop when the design feels comfortable and delivers value.

Signs of over-design:
- Layers with only one function
- Wrappers that add no abstraction
- Indirection that makes the code harder to follow

## Layer Organization by Change Frequency

| Layer | Content | Change Rate | Reusability |
|-------|---------|-------------|-------------|
| Top | Route handlers, CLI entry, UI events | High | Low |
| High | Business workflows, orchestration | Medium-High | Low |
| Mid | Domain rules, business logic | Medium | Medium |
| Low | Utility functions, data operations | Low | High |
| Bottom | Language built-ins, standard library | Never | Highest |

**Key insight**: Code at the bottom is more reusable and more important to test. Code at the top changes often and is easier to test (when calculations are extracted).

## Refactoring to Layers

### Technique: Extract and Lift

1. **Find a function** mixing multiple abstraction levels
2. **Extract** lower-level operations into separate functions
3. **Name** them to reflect their abstraction level
4. **Verify** the original function reads cleanly at one level

### Example: E-commerce Order Processing

```typescript
// BEFORE — all abstraction levels mixed
function handleOrderRequest(req: Request): Response {
  const body = JSON.parse(req.body);
  const items = body.items;
  let total = 0;
  for (const item of items) {
    const product = products.find(p => p.id === item.productId);
    if (!product) throw new Error("Not found");
    if (product.stock < item.qty) throw new Error("Out of stock");
    total += product.price * item.qty;
  }
  if (body.coupon === "SAVE10") total *= 0.9;
  const orderId = `ORD-${nextId++}`;
  orders.push({ id: orderId, items, total });
  return { status: 200, body: { orderId, total } };
}

// AFTER — stratified into layers

// Layer 2: Generic utilities
function lookupProduct(id: string, catalog: Product[]): Product | undefined {
  return catalog.find(p => p.id === id);
}

// Layer 3: Domain rules (Calculations)
function validateStock(product: Product, qty: number): boolean {
  return product.stock >= qty;
}

function lineTotal(price: number, qty: number): number {
  return price * qty;
}

function applyCoupon(total: number, coupon: string | undefined): number {
  return coupon === "SAVE10" ? total * 0.9 : total;
}

function calculateOrderTotal(
  items: OrderItem[],
  catalog: Product[],
  coupon?: string
): number {
  const subtotal = items.reduce((sum, item) => {
    const product = lookupProduct(item.productId, catalog);
    if (!product) throw new Error("Not found");
    if (!validateStock(product, item.qty)) throw new Error("Out of stock");
    return sum + lineTotal(product.price, item.qty);
  }, 0);
  return applyCoupon(subtotal, coupon);
}

// Layer 5: I/O shell (Action)
function handleOrderRequest(req: Request): Response {
  const body = JSON.parse(req.body);
  const total = calculateOrderTotal(body.items, products, body.coupon);
  const orderId = saveOrder(body.items, total);  // Action
  return { status: 200, body: { orderId, total } };
}
```

## Call Graph Visualization

Drawing a call graph helps verify stratification. Each function should only call functions at the same or lower level. Arrows crossing upward indicate a design problem.

```
handleOrderRequest (L5)
  ├── calculateOrderTotal (L3)
  │   ├── lookupProduct (L2)
  │   ├── validateStock (L3)
  │   ├── lineTotal (L3)
  │   └── applyCoupon (L3)
  └── saveOrder (L5)
```

All arrows point down or sideways — good stratification.

## Benefits

- **Testing**: Test each layer independently. Bottom layers are pure and easy to unit test.
- **Reuse**: Lower layers are generic and reusable across features.
- **Change isolation**: Modifying one layer has minimal impact on others.
- **Readability**: Each function reads at a consistent abstraction level.
- **Onboarding**: New developers can understand one layer at a time.
