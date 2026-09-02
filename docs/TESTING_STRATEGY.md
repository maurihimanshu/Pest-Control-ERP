# Testing Strategy & Quality Assurance Specification
## Pest Control Enterprise Resource Planning (ERP) Platform

**Document Version:** 1.0.0  
**Backend Test Framework:** JUnit 5 + Mockito + Testcontainers  
**Mobile Test Framework:** JUnit + Espresso + Room Migration Tests  
**Web Test Framework:** Vitest + React Testing Library + Playwright  
**Date:** September 2026  

---

## 1. Quality Assurance Philosophy & Testing Pyramid

```text
               ▲
              / \
             /E2E\       Playwright (Web) & Physical Device UAT
            /-----\
           / Integ \     Spring Boot + Testcontainers (Postgres, Redis, Rabbit)
          /---------\
         /   Unit    \   JUnit 5 + Mockito + Vitest (Isolated Domain Logic)
        /-------------\
```

---

## 2. Backend Testing Strategy (Spring Boot & Java 21)

### 2.1 Unit Tests (JUnit 5 & Mockito)
* **Domain Service Tests:** 100% test coverage on `PricingService`, `BookingStateMachine`, `CouponValidator`, and `AmcScheduleGenerator`.
* **Zero Mocking of POJOs:** Domain entities and calculations are tested with real values.

### 2.2 Integration Tests (Testcontainers)
Instead of mocking the database or message broker, integration tests run against real ephemeral Docker containers:
* **PostgreSQL Container:** Validates real Flyway SQL migrations, unique constraints, and JPA queries.
* **Redis Container:** Validates distributed locks (`Redisson`) and `@Cacheable` eviction.
* **RabbitMQ Container:** Validates message publishing and queue listener consumption.

```java
@SpringBootTest
@Testcontainers
class BookingServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Container
    static RabbitMQContainer rabbit = new RabbitMQContainer("rabbitmq:3.13-management-alpine");

    @Test
    void shouldCreateBookingAndEmitRabbitEvent() {
        // Real database transaction + RabbitMQ event test
    }
}
```

---

## 3. Mobile Testing Strategy (Android Apps)

* **Room Database Migration Testing:** Automated tests verify that upgrading SQLite schemas preserves local offline queues without data corruption.
* **Offline Sync Simulation:** Tests simulate network disconnects during job completion to verify `WorkManager` retry mechanics and idempotency.

---

## 4. Web Admin Testing Strategy (React & TypeScript)

* **Unit & Component Testing (Vitest & RTL):** Verifies form validation, table filters, and role-based component rendering.
* **End-to-End Testing (Playwright):** Validates the critical path: Admin Login $\rightarrow$ View Dispatch Board $\rightarrow$ Assign Technician $\rightarrow$ Generate Invoice.

---

## 5. Business-Invariant & Concurrency Integration Tests

The test suite must explicitly validate non-negotiable enterprise business invariants under concurrent load using Testcontainers:

1. **Booking Slot Capacity Race Condition:** 50 concurrent virtual threads attempt to reserve the final remaining capacity unit on an Agency Capacity Pool (`capacity = 5`, `booked_count = 4`); exactly 1 thread succeeds and 49 receive HTTP `409 Conflict`.
2. **Duplicate Payment Webhook Replay:** Multiple simultaneous deliveries of the exact same `(provider, gateway_event_id)` webhook payload execute; exactly 1 processes state mutation and all others return `HTTP 200 OK` without duplicate side-effects.
3. **Payment State Inversion Guard:** Webhooks arriving out of order (e.g. `payment.failed` after `payment.captured`) are rejected by domain state transition guards.
4. **Technician Duplicate Offline Sync:** Replaying the same `operation_id` returns the cached operation result without duplicating database mutations.
5. **Offline Completion vs. Administrative Cancellation:** Field completion during disconnection overrides a concurrent administrative cancellation and logs a record in `sync_conflicts`.
6. **Chemical Batch Inventory Concurrency:** Concurrent deductions across multiple visits for the same batch cannot drive `current_quantity_available` below zero; excess deductions throw `InsufficientInventoryException`.
7. **Coupon Usage & Per-User Limit Races:** Concurrent checkouts using the same single-use or per-user coupon cannot exceed configured limits.
8. **Multi-Tenancy Cross-Agency IDOR Attack:** Agency Manager from Agency A attempting to read or mutate Work Orders, Visits, or Inventory belonging to Agency B is rejected with HTTP `403 Forbidden` or `404 Not Found`.
9. **Presigned File Upload Authorization:** Direct attempts to request upload/download URLs for unassigned visits or other agencies are rejected.
10. **AMC Schedule Single-Instance Advisory Lock:** Concurrent scheduler executions across multiple application nodes acquire `pg_try_advisory_xact_lock` so only one node executes the generation.
11. **Transactional Outbox At-Least-Once Delivery:** Outbox relay worker survives simulated message broker restarts without losing pending events or producing phantom events.
12. **Invoice Numbering Concurrency:** High-concurrency invoice generation produces unique, monotonically allocated `INV-YYYY-NNNNN` numbers without duplicates. Gaps caused by PostgreSQL sequence allocation and rollback are recorded and accepted.

## 6. First Vertical Slice Executable Test Specification

Before implementing subsequent ERP submodules, the engineering team must implement and validate the following **Core Business Vertical Slice Test**:

```text
Customer Service Selection
       ↓
Atomic Capacity Reservation (PostgreSQL SELECT FOR UPDATE)
       ↓
Payment Authorization (Prepaid Razorpay / COD PENDING)
       ↓
Booking Confirmation (BookingConfirmed Outbox Event)
       ↓
Work Order Creation & Dispatch Assignment (TechnicianAssigned)
       ↓
Service Visit Scheduling
       ↓
Offline Mobile Field Execution (CameraX WebP, Chemical Usage, Keystore Signature)
       ↓
Idempotent Offline Synchronization (/api/v1/dispatch/visits/sync)
       ↓
Transactional Material Deduction (InventoryStockService in PostgreSQL)
       ↓
Service Visit Completion (ServiceVisitCompleted Outbox Event)
       ↓
Automated OpenPDF Invoice Generation (INV-YYYY-NNNNN in S3)
       ↓
Notification Multicast (FCM / SMS)
```

### Test Case Suite for First Vertical Slice:
1. **`V-SLICE-01` Happy Path End-to-End:** Validates complete lifecycle from booking checkout to S3 PDF invoice delivery and notification dispatch.
2. **`V-SLICE-02` Concurrent Slot Booking Race:** 10 concurrent threads attempt to reserve the 1 remaining slot in an agency capacity pool; exactly 1 succeeds, 9 fail with `409 Conflict`.
3. **`V-SLICE-03` Technician Time-Range Overlap Guard:** Verifies that assigning a named technician to an overlapping time window (e.g. 10:00–11:30 and 11:00–12:30) is rejected by PostgreSQL `ex_slot_employee_time_overlap` GiST exclusion constraint.
4. **`V-SLICE-04` Offline Sync with Keystore Signature:** Validates that field completion signed with device EC P-256 keypair is verified and committed; tampered payloads are rejected with HTTP 401.
5. **`V-SLICE-05` Webhook Reconciliation Under Network Drop:** Webhook delivery is blocked; scheduled reconciliation poller queries Razorpay mock API after 30 minutes and successfully converges payment to `PAID`.
6. **`V-SLICE-06` Consumer Inbox Deduplication:** RabbitMQ delivers duplicate `ServiceVisitCompleted` events; `inbox_events` ensures exactly one invoice is generated.
7. **`V-SLICE-07` Multi-Tenant Isolation (RLS):** Agency Manager B attempts to query Agency A's work orders; PostgreSQL Row Level Security returns 0 rows.

---

*Governed by enterprise software quality, automated Testcontainers integration, and continuous integration standards.*
