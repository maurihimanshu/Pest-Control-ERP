---
name: inventory-transactions
description: Designing the double-entry style inventory transaction ledger
category: database
triggers:
  - Design inventory ledger
  - Handle stock deductions
  - Record material usage
inputs:
  - Inventory requirement
outputs:
  - Inventory schema design
dependencies:
  - relational-modeling
related_skills:
  - domain/inventory
---

# Skill: Inventory Transactions

## Purpose
To design a robust, auditable inventory transaction ledger for the Pest Control ERP that accurately tracks material usage, prevents negative stock anomalies, and maintains FIFO (First-In-First-Out) batch deduction logic.

## When to Use / When NOT to Use
**Use When:** Modeling how chemicals, equipment, and materials move in and out of warehouses or technician vehicles.
**NOT to Use:** For non-consumable assets unless tracked via check-in/check-out logs, though this ledger focuses on consumable goods and stock levels.

## Required Context
Inventory cannot simply be an `UPDATE products SET stock = stock - X`. It must be a transactional ledger.

## Domain Rules & Constraints
1. **Double-Entry Style:** Every stock movement is a transaction. A deduction from a warehouse is an addition to a technician's trunk, or a consumption at a service visit.
2. **Ledger Table:** `inventory_transactions` must record:
   * `id UUID`
   * `product_id UUID`
   * `batch_id UUID` (for expiry tracking)
   * `location_id UUID` (source or destination)
   * `quantity DECIMAL(10,3)` (Positive for addition, negative for deduction)
   * `transaction_type VARCHAR` (e.g., 'PURCHASE', 'TRANSFER', 'CONSUMPTION', 'ADJUSTMENT')
   * `reference_id UUID` (e.g., `service_visit_id` if consumed during a job)
3. **FIFO Batch Deduction:** When stock is consumed, the system must automatically deduct from the oldest unexpired batch first.
4. **Transactional Consistency:** Material usage recorded during a `Service Visit` completion must be wrapped in the same database transaction as the inventory ledger insertion to prevent stock discrepancies.

## Business Rules
*   Stock levels at any location are calculated by summing the transactions for that location and product. (A materialized view or aggregate table `inventory_balances` can cache this for performance).
*   Negative stock should be strictly prevented via application logic and `CHECK` constraints on the balance table.

## Database Considerations
*   Use `DECIMAL(10,3)` or similar for quantities, especially for liquids/chemicals (e.g., 1.5 liters). Do NOT use floats.
*   Heavy indexing on `location_id`, `product_id`, and `created_at` in the transaction ledger is crucial for fast balance calculation.

## Validation Checklist
- [ ] Is the ledger append-only for stock movements?
- [ ] Are batches tracked for FIFO consumption?
- [ ] Are quantities stored as precise `DECIMAL` types?
- [ ] Is consumption transactionally tied to the `service_visit`?

## Common Mistakes
*   Updating a "current stock" column directly without recording the ledger transaction.
*   Using `FLOAT` instead of `DECIMAL`, leading to precision errors.
*   Allowing negative stock values in the balance cache.
*   Failing to link consumption back to the specific `service_visit_id`.

## Related Skills
- `domain/inventory`
- `domain/service-visit`
