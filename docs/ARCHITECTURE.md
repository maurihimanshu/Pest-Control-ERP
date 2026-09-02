# Architecture Reference
**Architecture Baseline:** 2026.09 (V2.1.0)  
**Implementation Status:** Documentation & Specification Baseline  
— Backend: Java 21 + Spring Boot 3.3.x Modular Monolith  
— Customer Mobile: Android Native (Java 21)  
— Technician Mobile: Android Native (Java 21, Offline-First)  
— Admin Web: React 18 + TypeScript (Vite + Ant Design)  

---

## 0. Architecture Authority & ADR Precedence Rule

The repository governance adheres to a strict hierarchy of authority:
1. **Accepted ADRs ([`docs/adr/`](adr/)):** Define binding architectural decisions and rationale.
2. **Canonical Architecture & Design Specifications ([`docs/`](./)):** Implement the decisions in the ADRs.
3. **Precedence Invariant:** If any ambiguity or contradiction arises between historical documentation and an accepted ADR, **the accepted ADR is the binding authority**.

---

## 1. System Context

The system consists of three client applications communicating with a central Spring Boot backend, supported by essential services.

```text
+-------------------+      +-------------------+      +-------------------+
| Customer App      |      | Technician App    |      | Admin Web App     |
| (Android/Java 21) |      | (Android/Java 21) |      | (React/TypeScript)|
+--------+----------+      +--------+----------+      +--------+----------+
         |                          |                          |
         | JSON/REST                | JSON/REST (Sync)         | JSON/REST
         v                          v                          v
+-------------------------------------------------------------------------+
|                          API Gateway / Nginx                            |
+-------------------------------------------------------------------------+
                                    |
+-------------------------------------------------------------------------+
|                        Spring Boot Application                          |
|                       (Modular Monolith - V1)                           |
|                                                                         |
|  [auth] [users] [customers] [employees] [agencies] [catalog]           |
|  [bookings] [dispatch] [payments] [inventory] [expenses] [amc]         |
|  [notifications] [support] [files] [reporting] [audit] [outbox]         |
+----+----------------------+-------------------+-------------------+-----+
     |                      |                   |                   |
     v                      v                   v                   v
+---------+           +------------+      +------------+      +-----------+
| Redis   |           | PostgreSQL |      | RabbitMQ   |      | S3/MinIO  |
| (Cache/ |           | (System of |      | (Async     |      | (Files &  |
|  Locks) |           |  Record)   |      |  Events)   |      |  Photos)  |
+---------+           +------------+      +------------+      +-----------+
```

## 2. Component Architecture & Canonical 18 Modules

The backend is built as a single deployable Spring Boot Modular Monolith.
**Layer Structure**: Controller → Service → Repository → Entity.
**Rule**: No cross-module `@Repository` or `@Entity` injection. Modules interact exclusively via public Service interfaces (`com.pestcontrol.modules.<module>.api.*`) or asynchronous Domain Events via `outbox_events` and RabbitMQ.

The canonical single source of truth for all 18 modules, their owned tables, public APIs, and event contracts is maintained in [`docs/MODULE_CATALOG.md`](MODULE_CATALOG.md).

```text
com.pestcontrol.modules
├── auth          ├── bookings      ├── notifications
├── users         ├── dispatch      ├── support
├── customers     ├── payments      ├── files
├── employees     ├── inventory     ├── reporting
├── agencies      ├── expenses      ├── audit
└── catalog       └── amc           └── outbox
```

## 3. Domain Boundaries & Aggregate Ownership

Strict separation of concerns across domain modules:
- **`bookings`**: Owns `bookings`, `booking_items`, `booking_events`, `coupons`, `coupon_redemptions`, `availability_slots`.
- **`dispatch`**: Owns `work_orders`, `service_visits` (1:N cardinality — one Work Order supports multiple Service Visits for initial/rescheduled/warranty/AMC visits), `service_checklists`, `offline_sync_logs`.
- **`payments`**: Owns `payments`, `payment_events`, `payment_transactions`, `invoices`, `invoice_items`. (Invoice generation is a component of the `payments` module in V1).
- **`inventory`**: Owns `chemical_products`, `chemical_batches`, `inventory_locations`, `inventory_transactions`, `service_material_usage`.
- **`catalog`**: Owns `service_categories`, `services`, `pricing_tiers`, `pricing_rules`. (Service catalog and pricing engine are subdomains within the `catalog` module).
- **`employees`**: Owns `employees`, `technician_skills`, `shift_schedules`. (`Employee` is the core identity; technicians are employees with the `TECHNICIAN` role).
- **`amc`**: Owns `amc_contracts`, `amc_schedules`.

## 4. Database Authority

**PostgreSQL 16 is THE system of record and the sole authority for business correctness.**
- **Concurrency & Invariants**: Handled strictly via PostgreSQL ACID transactions with pessimistic row locking (`SELECT FOR UPDATE`).
- **Cache in Redis**: Catalog items, pricing rules, and optional high-throughput pre-lock coordination. Under no circumstances is business correctness or state integrity delegated to Redis.
- **NEVER Cache as System of Record**: Payment state, booking status, inventory quantities.

## 5. Messaging Architecture & Canonical Outbox Rules

The system uses the Transactional Outbox Pattern to guarantee at-least-once delivery of domain events without distributed 2PC transactions. All locking, concurrency, and outbox rules are authoritatively specified in [`docs/CONCURRENCY_AND_IDEMPOTENCY.md`](CONCURRENCY_AND_IDEMPOTENCY.md).

```text
[Domain Service @Transactional] ──► (Updates PostgreSQL Entities)
                                ──► (Inserts into outbox_events table)
                                               │
                                       [COMMIT Transaction]
                                               │
                                               ▼
[Outbox Poller / Scheduler] ◄──────────────────┘
       │ (SELECT ... FOR UPDATE SKIP LOCKED)
       ▼
[RabbitMQ Exchange] ──► [Queue] ──► [Idempotent Consumer]
```

**Canonical Rule:** No domain transaction may publish directly to RabbitMQ. All events MUST be written to `outbox_events` in the same PostgreSQL transaction as the business mutation.

**Canonical Domain Events (PascalCase)**:
- `BookingCreated` (Source: `bookings` → Consumer: `notifications`)
- `BookingConfirmed` (Source: `bookings` → Consumer: `dispatch`, `notifications`)
- `WorkOrderCreated` (Source: `dispatch` → Consumer: `notifications`)
- `TechnicianAssigned` (Source: `dispatch` → Consumer: `notifications`)
- `TechnicianEnRoute` (Source: `dispatch` → Consumer: `notifications`)
- `ServiceVisitCompleted` (Source: `dispatch` → Consumer: `payments`, `notifications`, `amc`, `support`, `inventory`)
- `PaymentCompleted` (Source: `payments` → Consumer: `bookings`, `notifications`)
- `InvoiceGenerated` (Source: `payments` → Consumer: `notifications`)
- `AMCVisitGenerated` (Source: `amc` → Consumer: `dispatch`, `notifications`)

## 6. Authentication & Authorization

Firebase Auth handles identity verification.
**Flow**: Firebase Auth → ID Token → `FirebaseAuthenticationFilter` → PostgreSQL user lookup → Spring Security RBAC.
- **Identity**: Authenticated by Firebase.
- **Authorization**: Dictated by PostgreSQL roles.
- **User Deactivation**: If `is_active=false` in PostgreSQL, backend requests are rejected immediately, regardless of Firebase token validity.
- **Device Attestation**: Play Integrity API (Firebase App Check) is used for client integrity verification.

## 7. Tenant / Agency Model

Multi-agency model support:
- **Agency-Scoped Entities**: Employees, inventory, expenses, work orders, service visits, support tickets.
- **Domain Identifier**: Strictly **`agency_id`** across all database tables, DTOs, and domain models.
- **Security Rule**: Strict boundary enforcement. All queries on agency entities MUST filter by `agency_id` (`findByIdAndAgencyId`). Cross-agency access via ID manipulation is prohibited.

## 8. Android Client Architecture & Java 21 Toolchain Compatibility

The Customer and Technician Mobile Applications are developed natively in **Java 21**.

### 8.1 Android Build & Toolchain Specifications
* **Language Level:** Java 21 (`sourceCompatibility = JavaVersion.VERSION_21`, `targetCompatibility = JavaVersion.VERSION_21`)
* **Core Library Desugaring:** Enabled (`isCoreLibraryDesugaringEnabled = true`, `desugar_jdk_libs:2.0.4+`) to support Java 21 language features and `java.time` APIs on older Android runtime versions.
* **Compile SDK:** API Level 34 (Android 14) / 35 (Android 15)
* **Target SDK:** API Level 34 / 35
* **Minimum SDK:** API Level 26 (Android 8.0 Oreo — guarantees hardware-backed Keystore, modern networking, and notification channels)
* **Android Gradle Plugin (AGP):** Version 8.5.x or higher
* **Gradle Build Tool:** Version 8.7 or higher

### 8.2 Offline Synchronization (Technician App)
**Architecture**: Room DB → PendingOperation Queue → WorkManager → Spring Boot `/api/v1/dispatch/visits/sync`.
- **Payload Tracking**: `device_id`, `operation_id` (UUID idempotency key), `local_sequence` (BIGINT), `client_created_at`, `server_received_at`, `payload` (JSONB), `payload_version` (INT), `sync_status`.
- **Security & Idempotency**: Authenticated JWT + `device_id` + `operation_id` + monotonic sequence + server state validation + audit logging.
- **Conflict Handling**: If a field operation conflicts with authoritative server state (e.g. administrative cancellation), the event is recorded in `sync_conflicts` for manager review; it NEVER silently overwrites authoritative server state.
- **Local Security**: SQLCipher database encryption with master key managed via the **Android Keystore System**. Automated local data wipe on user logout or session invalidation.

## 9. Payment Architecture

Clients **never** declare payment success. Payment state is strictly updated via server-to-server Webhooks or direct server verification. Detailed in [`docs/PAYMENT_ARCHITECTURE.md`](PAYMENT_ARCHITECTURE.md).
- Deduplication key: `(provider, gateway_event_id)` in `payment_events`.
- Webhook updates payment state → Outbox event `PaymentCompleted` → Triggers `InvoiceGenerated`.
- PDF Engine: Strictly standardized on **`OpenPDF`**.

## 10. Inventory Concurrency

Inventory deduction is performed strictly inside the SAME PostgreSQL transaction as service visit completion. Detailed in [`docs/CONCURRENCY_AND_IDEMPOTENCY.md`](CONCURRENCY_AND_IDEMPOTENCY.md).
```text
BEGIN;
SELECT FOR UPDATE (lock chemical_batches row);
Validate current_quantity >= deduction AND NOT is_expired;
UPDATE chemical_batches SET current_quantity = current_quantity - deduction;
INSERT inventory_transactions;
INSERT service_material_usage;
UPDATE service_visits SET status = 'COMPLETED';
INSERT outbox_events(event_type='ServiceVisitCompleted', ...);
COMMIT;
```
Enforced by `CHECK (current_quantity_available >= 0)`. Downstream RabbitMQ listeners consume `ServiceVisitCompleted` purely for async reporting, low-stock threshold monitoring, and replenishment alerts.

## 11. Booking Slot Concurrency

Handled via `availability_slots` with `booked_count` and `capacity`.
- Two-tier model: Agency Capacity Pool (`employee_id IS NULL`, scoped by `agency_id` and `service_category_id`) reserved at booking confirmation vs Named Technician Slot (`employee_id IS NOT NULL`).
- Transactional `SELECT ... FOR UPDATE` during booking confirmation.
- Assignment of specific technicians to Work Orders is decoupled from slot reservation.

## 12. File Storage

Managed via `file_metadata` table in the `files` module.
- Presigned URLs are generated ONLY after verifying authorization in the backend.
- **Storage Abstraction:** Decoupled via `ObjectStoragePort` interface, with **AWS S3-compatible API** (AWS S3 / MinIO for local dev) as the default V1 provider.

## 13. Scheduling & Multi-Instance High Availability

- Spring `@Scheduled` for AMC daily cron (`01:00 UTC`), outbox polling, and batch expiry checks.
- Multi-instance single execution is guaranteed by PostgreSQL transaction-level advisory locks (`SELECT pg_try_advisory_xact_lock(...)`).


## 14. Observability

- Metrics: Spring Actuator + Micrometer + Prometheus.
- Tracing: MDC correlation ID (`X-Correlation-ID`).
- Logging: Structured JSON logs via Logback.
- Strict Rule: NEVER log PII, authentication tokens, or raw payment data.

## 15. Implementation Status & Roadmap

Refer to the top of this document. Currently in the Documentation / Architecture Baseline phase.
Modular Monolith is the architecture for V1. Future extraction into microservices will only occur when justified by scale, team size, or reliability constraints via the Strangler Fig Pattern.
