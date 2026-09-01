---
name: idempotency
description: Implements API idempotency to prevent duplicate operations.
category: backend
triggers:
  - make idempotent
  - handle retries
  - prevent duplicates
inputs:
  - mutable API endpoints (POST/PUT)
outputs:
  - idempotency mechanism
dependencies:
  - transaction-management
related_skills:
  - rest-controller
---

# Skill: Idempotency

## Purpose
To ensure that retrying a failed or timed-out request (due to network issues) does not result in duplicate state changes (e.g., double-charging a customer or creating duplicate bookings).

## Rules & Constraints
1. Clients MUST provide an `Idempotency-Key` header for critical mutations (Creation, Payment).
2. The backend must check this key against an idempotency store before processing.
3. Use a PostgreSQL table (e.g., `idempotency_keys`) or Redis with a TTL to store processed keys.
4. If a key is currently processing, return `409 Conflict` or wait.
5. If a key was already processed successfully, return the cached successful response.

## Step-by-Step Workflow
1. Intercept the request (via Filter or AOP interceptor).
2. Extract the `Idempotency-Key` header.
3. Attempt to insert the key into the datastore (using an atomic `INSERT IF NOT EXISTS` or Redis `SETNX`).
4. If insert fails, the key exists. Handle accordingly (return previous response).
5. If insert succeeds, proceed with the transaction.
6. Upon completion, update the idempotency record with the response payload and status.

## Validation Checklist
- [ ] Idempotency key is bound to the specific user/tenant to prevent collisions.
- [ ] Atomic operations are used to prevent race conditions.

## Common Mistakes
- Storing idempotency keys entirely in memory, which fails in multi-node deployments.
- Failing to capture and cache the actual response, resulting in identical operations returning different responses.
