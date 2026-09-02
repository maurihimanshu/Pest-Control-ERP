# Concurrency, Idempotency & Outbox Specification
**Architecture Baseline:** 2026.09 (V2.1.0)  
**Document Version:** 2.1.0  
**Implementation Status:** Documentation & Specification Baseline  
— Backend: Java 21 + Spring Boot 3.3.x  
— Primary Database: PostgreSQL 16  
— Cache & Coordination: Redis 7.2  
— Message Broker: RabbitMQ 3.13.x  

> **SOLE AUTHORITY DECLARATION:** This document is the single authoritative source of truth for concurrency control, database locking mechanisms, idempotency safeguards, and transactional message publication across the entire Pest Control ERP system. All code, domain services, background jobs, and subagent skills must strictly conform to the specifications herein.

---

## 1. Booking Slot Capacity & Concurrency Model

### 1.1 Conceptual Clarity: Agency Capacity Pool vs. Named Technician Slot
To support both self-service customer checkout and multi-technician dispatching without race conditions or premature resource locking:

1. **Availability Scope & Explicit Business Keys:**
   - **Agency Capacity Pool (`employee_id IS NULL`):** Default reservation unit for self-service customer checkout. Identified by the business key `(agency_id, service_category_id, service_date, start_time)`. Represents the aggregated concurrent appointment capacity of a branch/agency territory for a specific service category, date, and time window (e.g. `10:00–12:00`, `capacity = 5`).
   - **Named Technician Slot (`employee_id IS NOT NULL`):** Represents an individual technician's assigned calendar schedule (`capacity = 1`). Identified by the business key `(employee_id, service_date, start_time)`. Used when a customer or dispatcher explicitly requests a specific technician.
2. **Capacity Owner:** The Agency/Branch (`agency_id`) owning the postal code/territory manages the slot capacity pool.
3. **Reservation Unit:** Exactly 1 capacity unit is reserved per customer booking item during checkout (`booked_count = booked_count + 1`).
4. **Assignment Timing (Decoupled from Reservation):**
   - At booking confirmation: 1 capacity unit is deducted from the Agency Capacity Pool. The booking is `CONFIRMED`.
   - During dispatch window: The Dispatcher or Auto-Dispatch algorithm creates/assigns an operational `WorkOrder` and `ServiceVisit` to a specific, certified `Employee`. This decouples commercial booking confirmation from physical technician assignment.

### 1.2 Schema Definition & Database-Enforced Exclusion Constraints
```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE availability_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    service_category_id UUID REFERENCES service_categories(id) ON DELETE CASCADE,
    employee_id UUID REFERENCES employees(id) ON DELETE SET NULL, -- NULL = Agency Pool, NOT NULL = Named Tech
    service_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_range TSRANGE GENERATED ALWAYS AS (
        tsrange((service_date + start_time)::timestamp, (service_date + end_time)::timestamp, '[)')
    ) STORED,
    capacity INTEGER NOT NULL DEFAULT 1,
    booked_count INTEGER NOT NULL DEFAULT 0,
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_slot_time_valid CHECK (start_time < end_time),
    CONSTRAINT chk_slot_capacity_positive CHECK (capacity > 0),
    CONSTRAINT chk_slot_booked_nonneg CHECK (booked_count >= 0),
    CONSTRAINT chk_slot_capacity CHECK (booked_count <= capacity),
    -- PostgreSQL GiST Exclusion Constraint: Mathematically prevents overlapping time ranges for named technicians (P0-01)
    CONSTRAINT ex_slot_employee_time_overlap EXCLUDE USING gist (
        employee_id WITH =,
        slot_range WITH &&
    ) WHERE (employee_id IS NOT NULL AND is_blocked = FALSE)
);

-- Unique index for Agency Capacity Pools (prevents duplicate capacity pools for the same service category)
CREATE UNIQUE INDEX uq_slot_agency_pool 
ON availability_slots(agency_id, service_category_id, service_date, start_time) 
WHERE employee_id IS NULL;
```

### 1.3 Booking Confirmation Flow (Row-Level Locking)
```text
POST /api/v1/bookings/confirm
  BEGIN TRANSACTION
    -- Lock the specific availability slot row to prevent race conditions
    SELECT * FROM availability_slots 
    WHERE id = :slotId 
    FOR UPDATE;

    -- Evaluate business invariants under lock
    IF is_blocked OR booked_count >= capacity THEN
      ROLLBACK;
      THROW SlotUnavailableException("Selected time slot is fully booked");
    END IF;

    -- Atomically increment reservation count
    UPDATE availability_slots 
    SET booked_count = booked_count + 1,
        updated_at = NOW()
    WHERE id = :slotId;

    -- Update commercial booking status
    UPDATE bookings 
    SET status = 'CONFIRMED',
        updated_at = NOW()
    WHERE id = :bookingId;

    -- Record immutable booking event
    INSERT INTO booking_events(id, booking_id, event_type, actor_id, timestamp)
    VALUES (gen_random_uuid(), :bookingId, 'BOOKING_CONFIRMED', :actorId, NOW());

    -- Persist transactional outbox event
    INSERT INTO outbox_events(id, event_type, aggregate_type, aggregate_id, payload, publication_status)
    VALUES (gen_random_uuid(), 'BookingConfirmed', 'Booking', :bookingId, :eventPayloadJson, 'PENDING');
  COMMIT;
```

*(Optional Redis Layer)*: A short-TTL Redis key (`SET lock:slot:{id} NX EX 300`) may be acquired during the 5-minute checkout cart flow to provide optimistic UI reservations, but the PostgreSQL `SELECT ... FOR UPDATE` transaction remains the sole authoritative arbiter of capacity.

---

## 2. Inventory Concurrency, Transaction Orchestration & Offline Expiry

### 2.1 Core Architectural Rule & Cross-Module Contract
**Authoritative inventory deduction MUST execute strictly inside the SAME PostgreSQL transaction as service visit completion.**  
RabbitMQ is NEVER used to execute inventory deductions. RabbitMQ domain events (`ServiceVisitCompleted`, `LowStockAlert`) are dispatched AFTER commit exclusively for downstream asynchronous reactions (manager notifications, auto-replenishment purchase requests, analytics).

**Transaction Boundary Orchestration:**  
The `dispatch` module orchestrates the visit completion transaction by calling exported public service methods from the `inventory` module:
```java
// Inside com.pestcontrol.modules.dispatch.service.ServiceVisitCompletionService
@Transactional
public void completeVisit(UUID visitId, CompleteVisitRequest request) {
    // 1. Lock and update visit
    ServiceVisit visit = visitRepository.findByIdForUpdate(visitId);
    
    // 2. Invoke Inventory public API to deduct batch stock & record usage
    inventoryStockService.deductMaterialUsage(visitId, request.getMaterialsUsed());
    
    // 3. Mark visit completed and write outbox event
    visit.setStatus(ServiceVisitStatus.COMPLETED);
    outboxEventRepository.save(new OutboxEvent("ServiceVisitCompleted", "ServiceVisit", visitId, ...));
}
```

### 2.2 Material Deduction Flow & Offline Expiry Conflict Policy
```text
POST /api/v1/dispatch/visits/{visitId}/complete
  BEGIN TRANSACTION
    -- 1. Validate and lock visit
    SELECT * FROM service_visits WHERE id = :visitId FOR UPDATE;
    IF status = 'COMPLETED' THEN
      COMMIT;
      RETURN 200 OK; -- Idempotent completion check
    END IF;

    -- 2. Deduct all reported materials under pessimistic batch row locks
    FOR EACH material IN request.materialsUsed:
      SELECT * FROM chemical_batches 
      WHERE id = :material.batchId 
      FOR UPDATE;

      -- OFFLINE SYNC CONFLICT POLICY:
      -- If physical chemicals were used offline but the batch expired or stock depleted before sync:
      IF expiry_date < CURRENT_DATE THEN
        -- Record usage to preserve physical evidence, but flag conflict for branch manager
        INSERT INTO sync_conflicts(id, device_id, operation_id, agency_id, entity_type, entity_id, conflict_type, ...)
        VALUES (gen_random_uuid(), :deviceId, :opId, :agencyId, 'SERVICE_VISIT', :visitId, 'EXPIRED_BATCH_USED', ...);
      END IF;

      -- Deduct stock (or allow negative adjustment flagged with conflict if offline forced)
      UPDATE chemical_batches 
      SET current_quantity_available = current_quantity_available - :material.quantityUsed
      WHERE id = :material.batchId;

      -- Insert immutable inventory transaction ledger entry
      INSERT INTO inventory_transactions(id, batch_id, transaction_type, quantity_change, reference_visit_id, created_at)
      VALUES (gen_random_uuid(), :material.batchId, 'SERVICE_DEDUCTION', -:material.quantityUsed, :visitId, NOW());

      -- Insert visit material usage record (owned by inventory aggregate)
      INSERT INTO service_material_usage(id, service_visit_id, chemical_batch_id, quantity_used, dosage_rate, target_pest)
      VALUES (gen_random_uuid(), :visitId, :material.batchId, :material.quantityUsed, :material.dosageRate, :material.targetPest);
    END FOR;

    -- 3. Mark visit completed
    UPDATE service_visits 
    SET status = 'COMPLETED',
        completed_at = NOW(),
        updated_at = NOW()
    WHERE id = :visitId;

    -- 4. Insert transactional outbox event
    INSERT INTO outbox_events(id, event_type, aggregate_type, aggregate_id, payload, publication_status)
    VALUES (gen_random_uuid(), 'ServiceVisitCompleted', 'ServiceVisit', :visitId, :serviceCompletedJson, 'PENDING');
  COMMIT;
```

---

## 3. Payment Webhook Idempotency, Triaging & Retry Lifecycle

### 3.1 Webhook Deduplication Key: `(provider, gateway_event_id)`
Payment gateways (Razorpay, Stripe) deliver multiple webhook events per payment (`payment.authorized`, `payment.captured`, `payment.failed`, `refund.created`).  
**The sole mechanism for event deduplication is the unique constraint `(provider, gateway_event_id)` on the `payment_events` table.**  

### 3.2 Authoritative Webhook Triaging Pipeline
The server explicitly triages incoming webhook events into three distinct processing states:

```text
POST /api/v1/payments/webhooks/{provider}
  1. Cryptographic HMAC Signature Verification:
     - Razorpay: Verify X-Razorpay-Signature with webhook secret.
     - Stripe: Verify Stripe-Signature using Webhook.constructEvent().
     - If invalid signature -> Return HTTP 400 Bad Request immediately.

  2. Atomic Event Registration & Triaging:
     SELECT * FROM payment_events 
     WHERE provider = :provider AND gateway_event_id = :eventId 
     FOR UPDATE;

     IF EXISTS THEN
       -- Case A: Already successfully processed -> Idempotent success response
       IF processing_status = 'PROCESSED' THEN
         RETURN HTTP 200 OK;
       END IF;

       -- Case B: Currently being processed by another worker thread -> Suppress duplicate
       IF processing_status = 'PROCESSING' THEN
         RETURN HTTP 200 OK; -- Gateway will retry if current processing fails
       END IF;

       -- Case C: Previously FAILED -> Allow controlled re-execution upon redelivery
       UPDATE payment_events SET processing_status = 'PROCESSING', updated_at = NOW();
     ELSE
       -- Case D: New event -> Insert in PROCESSING state
       INSERT INTO payment_events (id, provider, gateway_event_id, gateway_payment_id, event_type, payload_hash, raw_payload, processing_status)
       VALUES (gen_random_uuid(), :provider, :eventId, :paymentId, :eventType, :hash, :payloadJson, 'PROCESSING');
     END IF;

  3. Business Transaction Execution:
     BEGIN TRANSACTION
       SELECT * FROM payments WHERE id = :internalPaymentId FOR UPDATE;

       -- Authoritative state machine transition validation
       ValidateStateTransition(currentStatus, newStatusFromEvent);

       UPDATE payments 
       SET status = :newPaymentStatus,
           paid_at = CASE WHEN :newPaymentStatus = 'PAID' THEN NOW() ELSE paid_at END,
           updated_at = NOW()
       WHERE id = :internalPaymentId;

       -- Mark payment event processed
       UPDATE payment_events 
       SET processing_status = 'PROCESSED',
           processed_at = NOW()
       WHERE provider = :provider AND gateway_event_id = :eventId;

       -- Persist domain outbox event
       INSERT INTO outbox_events(id, event_type, aggregate_type, aggregate_id, payload, publication_status)
       VALUES (gen_random_uuid(), 'PaymentCompleted', 'Payment', :internalPaymentId, :paymentEventJson, 'PENDING');
     COMMIT;

  4. Error Handling:
     ON EXCEPTION:
       UPDATE payment_events 
       SET processing_status = 'FAILED', 
           error_message = :exceptionMessage,
           updated_at = NOW()
       WHERE provider = :provider AND gateway_event_id = :eventId;
       RETURN HTTP 500 Internal Server Error; -- Triggers gateway backoff retry

---

### 3.3 Payment Gateway Scheduled Reconciliation (P1-03)

Payment correctness does not depend exclusively on webhook delivery. To protect against lost, delayed, or out-of-order webhooks:
1. **Reconciliation Poller:** A Spring `@Scheduled` background worker runs every 15 minutes:
   ```sql
   SELECT * FROM payments 
   WHERE payment_method = 'ONLINE_GATEWAY' 
     AND status = 'PENDING' 
     AND created_at < (NOW() - INTERVAL '30 minutes')
     AND created_at > (NOW() - INTERVAL '72 hours')
   FOR UPDATE SKIP LOCKED;
   ```
2. **Gateway State Verification:** For each stuck payment, the worker queries the gateway API (`GET /v1/orders/{gateway_order_id}/payments` on Razorpay or Stripe PaymentIntents API).
3. **State Convergence:**
   - If gateway reports captured/succeeded $\rightarrow$ executes authoritative payment completion transition and writes outbox event `PaymentCompleted`.
   - If gateway reports failed/expired $\rightarrow$ transitions payment to `FAILED`.
   - If gateway reports still unpaid $\rightarrow$ remains `PENDING` until 72-hour expiration window closes.

---

## 4. Transactional Outbox Pattern & Canonical Event Identity

### 4.1 Canonical Outbox Contract & Event Identity
- **Sole Deduplication Identity:** The canonical identifier of every domain event is `outbox_events.id` (UUID v4), populated at insert time. Downstream consumers deduplicate exclusively on `event.id`. No volatile timestamps are used for identity.
- **Relay Delivery:**
```text
   Domain @Transactional Method (e.g., Booking, Dispatch, Payment)
        │
        ├── 1. Mutate domain entity (PostgreSQL)
        ├── 2. Insert outbox_events row with unique UUID (Same Transaction)
        └── 3. COMMIT Database Transaction
                     │
                     ▼ (PostgreSQL durability guaranteed)
        Independent Outbox Relay Worker (Spring @Scheduled Poller)
        │
        ├── 4. SELECT * FROM outbox_events WHERE publication_status = 'PENDING' 
        │      FOR UPDATE SKIP LOCKED LIMIT 100;
        ├── 5. Publish domain event to RabbitMQ Exchange
        ├── 6. On broker ACK -> UPDATE outbox_events SET publication_status = 'PUBLISHED', published_at = NOW();
        └── 7. On broker NACK/Error -> UPDATE outbox_events SET retry_count++, last_error = ...;
```
### 4.2 Non-Negotiable Publication Rules
1. **NO direct RabbitMQ publishing from business transactions.** Direct calls to `RabbitTemplate.convertAndSend()` inside `@Transactional` methods are strictly forbidden.
2. **NO unreliable event listeners.** Spring `@TransactionalEventListener(phase = AFTER_COMMIT)` without outbox persistence is forbidden because broker downtime causes silent event loss.
3. **Database and Outbox Row Commit Atomically.** If the domain transaction fails, the outbox record is rolled back, preventing phantom message publishing.
4. **Guaranteed At-Least-Once Delivery.** The outbox relay guarantees delivery. Downstream RabbitMQ consumers must be idempotent.

### 4.3 Outbox Schema
```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,        -- PascalCase: 'BookingConfirmed', 'PaymentCompleted', etc.
    aggregate_type VARCHAR(100) NOT NULL,    -- 'Booking', 'Payment', 'ServiceVisit'
    aggregate_id UUID NOT NULL,
    payload JSONB NOT NULL,
    payload_version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    publication_status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, PUBLISHED, FAILED
    retry_count INT NOT NULL DEFAULT 0,
    last_error TEXT
);

CREATE INDEX idx_outbox_pending_poller 
ON outbox_events(publication_status, created_at) 
WHERE publication_status = 'PENDING';
```

### 4.4 RabbitMQ Consumer Idempotency & Inbox Pattern (P1-04)

Every material, side-effecting domain consumer (Notifications, Invoicing, AMC, Inventory Alerting) implements the canonical **Inbox Pattern** to guarantee exactly-once business side effects under at-least-once message delivery:

```sql
CREATE TABLE inbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_name VARCHAR(100) NOT NULL,
    event_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'PROCESSED',
    error_message TEXT,
    CONSTRAINT uq_consumer_event UNIQUE (consumer_name, event_id)
);
CREATE INDEX idx_inbox_consumer ON inbox_events(consumer_name, event_id);
```

**Consumer Execution Workflow:**
```text
RabbitMQ Message Received (event_id, event_type, payload)
  │
  ├── 1. BEGIN TRANSACTION
  ├── 2. INSERT INTO inbox_events(consumer_name, event_id, event_type, payload)
  │      VALUES (:consumerName, :eventId, :eventType, :payload)
  │      ON CONFLICT (consumer_name, event_id) DO NOTHING;
  │
  ├── 3. IF rows_affected == 0 THEN
  │        ROLLBACK;
  │        ACK message to RabbitMQ (duplicate message suppressed);
  │        RETURN;
  │      END IF;
  │
  ├── 4. Execute domain side effect (e.g. generate invoice, send push alert)
  └── 5. COMMIT TRANSACTION
```

---

## 5. Offline Field Operation Idempotency, Security & Conflict Schema

Technician mobile apps execute actions offline in local SQLite/Room storage.

### 5.1 Cryptographic Trust Model & Device-Bound Payload Signing (P0-02)
To secure offline mutations against tampering, client replay, and rogue device injection:
1. **Device Enrollment:** Upon login, the Technician App generates an **EC P-256 Keypair inside the hardware-backed Android Keystore**. The public key is registered in PostgreSQL under `technician_devices(device_id, public_key_pem)`.
2. **High-Risk Operation Signing:** For critical field operations (`START_VISIT`, `COMPLETE_VISIT`, `LOG_CHEMICALS`), the device signs the serialized operation payload (`SHA256withECDSA`) using the Keystore private key, sending the signature in the `X-Device-Signature` HTTP header.
3. **Server Verification:** The sync controller verifies the cryptographic signature against the stored device public key before executing the business transaction.

### 5.2 Operation Envelope Structure
Each queued mobile mutation generates a deterministic action record:
- `operation_id` (UUID v4): Unique client-generated idempotency key for the atomic action.
- `device_id` (UUID): Registered hardware device identifier linked to the technician.
- `local_sequence` (BIGINT): Monotonically increasing sequence number per device.
- `client_created_at` (TIMESTAMPTZ): Device clock timestamp when the physical action occurred.
- `operation_type` (VARCHAR): e.g. `START_VISIT`, `COMPLETE_VISIT`, `LOG_CHEMICALS`.
- `payload` (JSONB): Action parameters.
- `payload_version` (INT): Schema version of the payload (enables server backward compatibility, P2-05).

### 5.3 Server Sync Handler & Conflict Tracking
```sql
CREATE TABLE sync_conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL,
    operation_id UUID NOT NULL,
    agency_id UUID NOT NULL REFERENCES agencies(id),
    entity_type VARCHAR(100) NOT NULL, -- 'SERVICE_VISIT', 'WORK_ORDER'
    entity_id UUID NOT NULL,
    conflict_type VARCHAR(50) NOT NULL, -- 'CLIENT_OVERRIDE_ON_CANCELLED', 'STALE_STATE_COLLISION', 'EXPIRED_BATCH_USED'
    client_state JSONB NOT NULL,
    server_state JSONB NOT NULL,
    resolution_status VARCHAR(50) NOT NULL DEFAULT 'OPEN', -- 'OPEN', 'AUTO_RESOLVED', 'MANUALLY_RESOLVED'
    resolved_by UUID REFERENCES users(id),
    resolution_notes TEXT,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_sync_conflicts_agency ON sync_conflicts(agency_id, resolution_status);
```
1. Validate device registration, JWT employee identity, and Keystore `X-Device-Signature`.
2. Process queued operations in strict `local_sequence` order.
3. Check `operation_id` against `offline_sync_logs`:
   - If `operation_id` is already logged as processed -> Return previous result (safe replay).
   - If `operation_id` is new -> Execute domain operation in a database transaction and log `operation_id`.
4. Conflict Handling: Completed physical field work conflicting with server cancellation or stock expiration is recorded in `sync_conflicts` for manager audit; it NEVER silently overwrites authoritative server state.


---

## 6. General API Request Idempotency & Request Fingerprinting

Mutating HTTP POST requests from web and mobile clients (e.g. `POST /api/v1/bookings`, `POST /api/v1/payments/initiate`) must supply an `Idempotency-Key` header.

To prevent payload tampering or accidental key reuse across different requests, the backend stores a deterministic SHA-256 fingerprint (`request_hash`) of the request payload and binds the key to the agency, user, and endpoint:

```sql
CREATE TABLE idempotency_keys (
    key VARCHAR(255) PRIMARY KEY,
    agency_id UUID REFERENCES agencies(id),
    user_id UUID NOT NULL REFERENCES users(id),
    http_method VARCHAR(10) NOT NULL,
    request_path VARCHAR(500) NOT NULL,
    request_hash VARCHAR(64) NOT NULL, -- SHA-256 of normalized request body
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, COMPLETED, FAILED
    response_status INT,
    response_headers JSONB,
    response_body JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours')
);

CREATE INDEX idx_idempotency_lookup ON idempotency_keys(agency_id, user_id, request_path, key);
CREATE INDEX idx_idempotency_expires ON idempotency_keys(expires_at);
```

**Fingerprint Validation Invariants:**  
- **Same Key + Same `request_hash`:** Returns the exact previously cached HTTP response status and body without re-executing business logic.
- **Same Key + Different `request_hash`:** Server immediately rejects the call with HTTP `422 Unprocessable Entity` (`IDEMPOTENCY_KEY_PAYLOAD_MISMATCH`).

---

## 7. Multi-Tenancy Hardening & IDOR Prevention

### 7.1 Non-Negotiable Repository Rule
To eliminate the risk of developer omission of tenant checks:
- **FORBIDDEN:** Generic `findById(UUID id)` calls on agency-scoped entities (`work_orders`, `service_visits`, `inventory`, `expenses`, `support_tickets`).
- **MANDATORY:** All queries and updates on agency-scoped entities MUST use explicit tenant-bound methods:
  ```java
  Optional<WorkOrder> findByIdAndAgencyId(UUID id, UUID agencyId);
  Optional<ServiceVisit> findByIdAndAgencyId(UUID id, UUID agencyId);
  ```
  or inherit from an enforced `AgencyScopedRepository<T, ID>` base interface.
- **Automated IDOR Tests:** Every agency-scoped resource endpoint must include integration tests attempting cross-agency ID access with verification of HTTP `403 Forbidden` / `404 Not Found`.

---

## 8. Database-Enforced Audit Log Immutability

Audit log records are immutable by database definition, not merely by application convention:

```sql
CREATE OR REPLACE FUNCTION trg_audit_logs_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_logs entries are strictly immutable and cannot be updated or deleted';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_logs_no_update_delete
BEFORE UPDATE OR DELETE ON audit_logs
FOR EACH ROW EXECUTE FUNCTION trg_audit_logs_immutable();

-- Revoke mutation permissions from the application database user role
REVOKE UPDATE, DELETE, TRUNCATE ON audit_logs FROM pestcontrol_app_user;
```

---

## 9. AMC Schedule Uniqueness & Multi-Instance Scheduler HA

### 9.1 Database Uniqueness Constraint
```sql
ALTER TABLE amc_schedules 
ADD CONSTRAINT uq_amc_schedule_contract_seq UNIQUE (amc_contract_id, visit_sequence);
```

### 9.2 Scheduler High Availability (PostgreSQL Advisory Lock)
To safely run Spring `@Scheduled` cron jobs across multiple scaled application nodes without duplicate work order generation:
```java
@Scheduled(cron = "0 0 1 * * ?") // Daily at 01:00 UTC
@Transactional
public void generateDueAMCWorkOrders() {
    // Acquire PostgreSQL transaction-level advisory lock
    Boolean lockAcquired = entityManager.createNativeQuery(
        "SELECT pg_try_advisory_xact_lock(hashtext('amc_visit_scheduler_lock'))"
    ).getSingleResult().equals(Boolean.TRUE);

    if (!lockAcquired) {
        log.info("Another cluster node is executing the AMC generation job. Skipping.");
        return;
    }

    // Execute idempotent generation under advisory lock...
}
```

---

## 10. Coupon Arbitrary Per-User Limit Concurrency

To support arbitrary `perUserLimit` (e.g. `perUserLimit = 3` or `unlimited`):
```text
POST /api/v1/bookings
  BEGIN TRANSACTION
    -- 1. Lock coupon record
    SELECT * FROM coupons WHERE code = :code FOR UPDATE;
    
    -- 2. Check global usage limit
    IF usage_limit IS NOT NULL AND usage_count >= usage_limit THEN
      ROLLBACK; THROW CouponDepletedException();
    END IF;

    -- 3. Check customer-specific usage limit under lock
    SELECT COUNT(*) FROM coupon_redemptions 
    WHERE coupon_id = :couponId AND customer_id = :customerId;
    
    IF per_user_limit IS NOT NULL AND customer_redemptions >= per_user_limit THEN
      ROLLBACK; THROW CouponUserLimitExceededException();
    END IF;

    -- 4. Apply coupon and record redemption
    UPDATE coupons SET usage_count = usage_count + 1 WHERE id = :couponId;
    INSERT INTO coupon_redemptions(id, coupon_id, customer_id, booking_id, redeemed_at)
    VALUES (gen_random_uuid(), :couponId, :customerId, :bookingId, NOW());
  COMMIT;
```

---

## 11. Optimistic Locking on Mutating Entities

All frequently modified domain entities (`bookings`, `work_orders`, `service_visits`, `payments`, `amc_contracts`) declare JPA `@Version private Long version;`. Concurrent conflicting updates throw `OptimisticLockException`, returning HTTP `409 Conflict` to prompt client refresh.
