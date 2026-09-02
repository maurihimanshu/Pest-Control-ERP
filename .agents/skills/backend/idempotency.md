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
1. Clients MUST provide an `Idempotency-Key` header for critical mutations (Bookings, Payments, Offline Sync).
2. **Authoritative Idempotency Store (PostgreSQL):** All financial, booking, and offline mutations MUST persist idempotency keys and cached response payloads in PostgreSQL (`idempotency_keys` table). Redis is used strictly for ephemeral rate limiting / throttling, NOT as the sole idempotency store for business transactions.
3. Bind the idempotency record to `(agency_id, user_id, http_method, request_path, request_hash)`.
4. If a request is received with the same key and identical payload `request_hash`:
   - If `status = 'COMPLETED'`, return the cached HTTP response status and body immediately.
   - If `status = 'PENDING'`, return `HTTP 409 Conflict` or wait.
5. If a request is received with the same key but a different `request_hash`, reject with `HTTP 422 Unprocessable Entity` (`IDEMPOTENCY_KEY_PAYLOAD_MISMATCH`).

## Step-by-Step Workflow
1. Intercept mutating request in `IdempotencyFilter` / AOP interceptor.
2. Extract `Idempotency-Key` header and compute SHA-256 hash of the normalized request body.
3. Execute atomic PostgreSQL insert:
   ```sql
   INSERT INTO idempotency_keys (key, agency_id, user_id, http_method, request_path, request_hash, status)
   VALUES (:key, :agencyId, :userId, :method, :path, :hash, 'PENDING')
   ON CONFLICT (key) DO NOTHING;
   ```
4. If row was not inserted:
   - Query existing row. If `request_hash` differs $\rightarrow$ throw `IdempotencyPayloadMismatchException`.
   - If completed $\rightarrow$ return cached `response_body` and `response_status`.
5. If row was inserted $\rightarrow$ execute `@Transactional` business logic.
6. On success, update `idempotency_keys` with `status = 'COMPLETED'`, `response_status`, and `response_body`.

## Validation Checklist
- [ ] Idempotency is persisted authoritatively in PostgreSQL (`idempotency_keys`).
- [ ] Keys are bound to agency, user, path, and payload fingerprint.
- [ ] Payload mismatch throws HTTP 422.

## Common Mistakes
- Storing critical financial idempotency keys only in Redis, which causes silent duplicates on Redis eviction or restart.
- Not verifying the request body SHA-256 fingerprint, allowing key reuse across different operations.

