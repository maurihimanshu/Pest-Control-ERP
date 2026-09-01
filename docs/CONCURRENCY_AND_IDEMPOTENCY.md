# Concurrency & Idempotency Reference
Implementation Status: Documentation / Architecture Baseline
— Backend: Not implemented
— Customer Android: Not implemented
— Technician Android: Not implemented
— Admin Web: Not implemented

This document is the authoritative source for concurrency handling, locking mechanisms, and idempotency across the Pest Control ERP system.

## 1. Booking Slot Concurrency

Booking slots must be protected from double-booking using PostgreSQL row-level locks.

**Schema**:
```sql
CREATE TABLE availability_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    agency_id UUID REFERENCES agencies(id),
    employee_id UUID REFERENCES employees(id),
    capacity INTEGER NOT NULL DEFAULT 1,
    booked_count INTEGER NOT NULL DEFAULT 0 CHECK (booked_count >= 0),
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_slot_employee_time ON availability_slots(employee_id, service_date, start_time);
```

**Flow (Confirmation)**:
```text
POST /api/v1/bookings/confirm
  BEGIN TRANSACTION
    SELECT * FROM availability_slots WHERE id = ? FOR UPDATE  -- row lock
    CHECK: booked_count < capacity AND NOT is_blocked
    IF not available: ROLLBACK → throw SlotUnavailableException → HTTP 409
    UPDATE availability_slots SET booked_count = booked_count + 1
    UPDATE bookings SET status = 'CONFIRMED'
    INSERT booking_events(type='CONFIRMED')
    INSERT outbox_events(type='BookingConfirmed', ...)
  COMMIT
```
*(Optional pre-lock)*: Short-TTL Redis key to reduce DB lock contention during browsing. DB transaction remains authoritative.

## 2. Inventory Deduction Concurrency

Transactional deduction ensures inventory levels never fall below zero.

**Schema Constraint**:
```sql
ALTER TABLE chemical_batches ADD CONSTRAINT chk_batch_qty_nonneg CHECK (current_quantity >= 0);
```

**Flow**:
```text
POST /api/v1/dispatch/visits/{id}/complete
  BEGIN TRANSACTION
    FOR EACH material IN request.materialsUsed:
      SELECT * FROM chemical_batches WHERE id = ? FOR UPDATE
      IF batch.is_expired OR batch.current_quantity < used_qty:
        ROLLBACK → throw InsufficientInventoryException
      UPDATE chemical_batches SET current_quantity = current_quantity - used_qty
      INSERT inventory_transactions(type='SERVICE_DEDUCTION', batch_id, qty_change=-used_qty, ref_visit_id)
      INSERT service_material_usage(visit_id, batch_id, used_qty, ...)
    UPDATE service_visits SET status = 'COMPLETED'
    INSERT outbox_events(type='ServiceCompleted', ...)
  COMMIT
```
- **Rollbacks**: If a visit is cancelled after completion, a compensating transaction restores batch quantity (creates a REVERSAL `inventory_transaction`).
- **Duplicate Sync**: Checked via `operation_id` idempotency.

## 3. Payment Webhook Idempotency

Webhooks from payment providers (Razorpay, Stripe) must be processed idempotently. Client payment results are NEVER trusted.

**Schema**:
```sql
CREATE TABLE payment_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID REFERENCES payments(id),
    provider VARCHAR(50) NOT NULL,          -- 'RAZORPAY', 'STRIPE'
    gateway_event_id VARCHAR(255) NOT NULL, -- from webhook
    gateway_payment_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,       -- 'payment.captured', 'payment.failed'
    payload_hash VARCHAR(64),               -- SHA-256 of raw payload
    received_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    processing_status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, PROCESSED, FAILED, SKIPPED
    CONSTRAINT uq_payment_event UNIQUE (provider, gateway_event_id)
);
```

**Flow**:
```text
POST /api/v1/payments/webhook/{provider}
  1. Verify HMAC-SHA256 signature (reject if invalid → HTTP 400)
  2. Extract event_id from provider payload
  3. INSERT INTO payment_events (provider, gateway_event_id, ...) ON CONFLICT DO NOTHING 
     → if 0 rows affected: already processed → return HTTP 200
  4. BEGIN TRANSACTION
       Validate payment state transition
       UPDATE payments SET status = ?
       UPDATE payment_events SET processing_status = 'PROCESSED'
       INSERT audit_logs(...)
       INSERT outbox_events(type='PaymentCompleted', ...)
     COMMIT
  5. Return HTTP 200
```
- Always poll `GET /api/v1/payments/{id}` for authoritative server state.

## 4. Outbox Pattern

Guarantees at-least-once message delivery without two-phase commits.

**Schema**:
```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,        -- 'BookingConfirmed', 'PaymentCompleted'
    aggregate_type VARCHAR(100) NOT NULL,    -- 'Booking', 'Payment'
    aggregate_id UUID NOT NULL,
    payload JSONB NOT NULL,
    payload_version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    publication_status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, PUBLISHED, FAILED
    retry_count INT DEFAULT 0,
    last_error TEXT,
    CONSTRAINT uq_outbox_event UNIQUE (event_type, aggregate_id, created_at)
);
CREATE INDEX idx_outbox_pending ON outbox_events(publication_status, created_at) WHERE publication_status = 'PENDING';
```
- **Publisher**: Spring `@Scheduled` job polls `PENDING` events every 1-5 seconds → publishes to RabbitMQ → marks `PUBLISHED`.
- **Consumers**: Must check event IDs (idempotent).

## 5. Offline Operation Idempotency

Resolves conflicts between the Technician App (offline-first) and the backend.

**Operation Fields (Android Room DB)**:
`operation_id` (UUID v4), `device_id`, `event_id`, `local_sequence` (BIGINT), `client_created_at`, `server_received_at`, `operation_type`, `payload`, `payload_version`, `retry_count`, `sync_status`, `last_sync_error`.

**Sync Flow (`POST /api/v1/dispatch/visits/sync`)**:
1. Process operations in `local_sequence` order.
2. Check `operation_id` against server-side processed operations.
3. If duplicate `operation_id` → Return previously computed result (do not re-process).
4. **Conflict Detection**: If server-side state is newer/conflicting:
   - Create conflict record.
   - Notify DISPATCHER/AGENCY_MANAGER.
   - Do NOT silently overwrite server state.

**Security**: NO cryptographic signing of payloads. Replaced by:
- Firebase JWT (identity).
- `device_id` (linked to employee).
- `operation_id` (replay prevention).
- `local_sequence` (ordering).
- Server-side validation and audit logging.

## 6. API Request Idempotency

General mechanism for preventing duplicate external requests.

**Schema**:
```sql
CREATE TABLE idempotency_keys (
    key VARCHAR(255) PRIMARY KEY,
    user_id UUID NOT NULL,
    request_path VARCHAR(500) NOT NULL,
    response_status INT NOT NULL,
    response_body JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'
);
```
**Headers**: `Idempotency-Key: <client-generated-uuid>`. Required for booking creation, payment initiation, invoice generation, AMC visit generation.

## 7. Optimistic Locking

Used for entities that can be concurrently modified. Enforced by JPA `@Version`.
```java
@Version
private Long version;
```
- **Throws**: `OptimisticLockException` → HTTP 409 Conflict → Client should retry.
- **Used for**: `bookings`, `work_orders`, `service_visits`, `payments`, `amc_contracts`.

## 8. Coupon Redemption Concurrency

Ensures usage limits are strictly enforced.

**Schema**:
```sql
CREATE TABLE coupon_redemptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coupon_id UUID NOT NULL REFERENCES coupons(id) ON DELETE RESTRICT,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE RESTRICT,
    redeemed_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_coupon_customer UNIQUE (coupon_id, customer_id)  -- for perUserLimit=1
);
```
- **Higher Limits**: Requires `COUNT` redemptions per customer within a `SELECT FOR UPDATE` transaction on the `coupon` row.
- **Global Limits**: `UPDATE coupons SET used_count = used_count + 1 WHERE id = ? AND used_count < max_uses`. Checked atomically.
