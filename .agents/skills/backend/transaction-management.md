---
name: transaction-management
description: Manages Spring @Transactional boundaries, propagation, and isolation.
category: backend
triggers:
  - configure transactions
  - handle data consistency
inputs:
  - service methods
outputs:
  - transactional boundaries configured
dependencies:
  - service-layer
related_skills:
  - repository-layer
---

# Skill: Transaction Management

## Purpose
To ensure database operations complete successfully as a unit or rollback completely, preserving data integrity in PostgreSQL.

## Rules & Constraints
1. Place `@Transactional` at the Service layer, NOT the Repository or Controller layer.
2. Read-only operations should use `@Transactional(readOnly = true)` for performance and to route to read replicas if configured.
3. Be aware of proxy limitations (self-invocation does NOT trigger transactional behavior unless explicitly handled via `AopContext` or self-injection).
4. Default propagation (`REQUIRED`) is usually sufficient; use `REQUIRES_NEW` only when explicitly needing an independent transaction (e.g., audit logging).

## Step-by-Step Workflow
1. Identify the entry point of the business transaction.
2. Annotate the method with `@Transactional`.
3. If it throws a checked exception that MUST trigger a rollback, specify `@Transactional(rollbackFor = Exception.class)`. (By default, Spring only rolls back on unchecked/Runtime exceptions).
4. Keep the transaction short. Do NOT perform remote HTTP calls inside the transaction block if possible.

## Validation Checklist
- [ ] Read-only flag used where appropriate.
- [ ] Rollback behavior is correctly configured.
- [ ] No expensive remote I/O inside the transaction.

## Common Mistakes
- Calling external APIs (e.g., Stripe, FCM) inside a database transaction, which can lock tables for a long time if the network is slow.
