# Architecture Reference
Implementation Status: Documentation / Architecture Baseline
— Backend: Not implemented
— Customer Android: Not implemented
— Technician Android: Not implemented
— Admin Web: Not implemented

This is the PRIMARY architectural reference for the Pest Control ERP system. All other architectural documents defer to this one.

## 1. System Context

The system consists of three client applications communicating with a central Spring Boot backend, supported by essential services.

```text
+-------------------+      +-------------------+      +-------------------+
| Customer App      |      | Technician App    |      | Admin Web App     |
| (Android/Kotlin)  |      | (Android/Kotlin)  |      | (React/TypeScript)|
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
|  [Security/Auth] [Booking] [Dispatch] [Inventory] [Payment] [AMC] ...   |
+----+----------------------+-------------------+-------------------+-----+
     |                      |                   |                   |
     v                      v                   v                   v
+---------+           +------------+      +------------+      +-----------+
| Redis   |           | PostgreSQL |      | RabbitMQ   |      | S3/GCS    |
| (Cache) |           | (System of |      | (Outbox &  |      | (Files &  |
+---------+           |  Record)   |      |  Events)   |      |  Photos)  |
                      +------------+      +------------+      +-----------+
```

## 2. Component Architecture
The backend is built as a Spring Boot Modular Monolith.
**Layer Structure**: Controller → Service → Repository → Entity.
**Rule**: No cross-module `@Repository` injection. Modules interact exclusively via public Service interfaces or asynchronous Domain Events.

Modules (18 Total):
1. Security/Auth
2. Users
3. Agency (Multi-tenant support)
4. Catalog (Services, Pricing)
5. Booking
6. Dispatch (Work Orders, Visits)
7. Inventory
8. Payments
9. AMC (Annual Maintenance Contracts)
10. Notifications
11. Support
12. Files
13. Audit
14. Outbox
15. Reporting
16. Geolocation
17. Integration (Third-party ERPs/CRMs)
18. Configuration

## 3. Domain Boundaries
Strict separation of concerns across modules:
- **Booking**: Owns `bookings`, `booking_items`, `booking_events`, `coupons`, `coupon_redemptions`.
- **Dispatch**: Owns `work_orders`, `service_visits` (1:N — one Work Order may have multiple Service Visits for failed/rescheduled/warranty/AMC visits), `service_checklists`.
- **Payments**: Owns `payments`, `payment_events`, `invoices`, `invoice_items`.
- **Inventory**: Owns `chemical_products`, `chemical_batches`, `inventory_transactions`, `service_material_usage`.
- **AMC**: Owns `amc_contracts`, `amc_schedules`.

## 4. Database Authority
**PostgreSQL 16 is THE system of record.**
- **Cache in Redis**: Catalog items, pricing rules, slot availability (optimistic UI caching).
- **NEVER Cache**: Payment state, booking status, inventory quantities used for financial reporting.

## 5. Messaging Architecture
The system uses the Outbox Pattern to guarantee at-least-once delivery of domain events without distributed transactions.

```text
[Module A Service] --> (Updates PostgreSQL Entities)
                   --> (Inserts into outbox_events)
                          |
[Outbox Poller] <---------+
      |
      v
[RabbitMQ Exchange] ---> [Queue B] ---> [Module B Consumer]
```
**Key Domain Events**:
- `BookingConfirmed` (Source: Booking → Consumer: Dispatch, Notification)
- `WorkOrderCreated` (Source: Dispatch → Consumer: Notification)
- `ServiceCompleted` (Source: Dispatch → Consumer: Inventory, Payments)
- `PaymentCompleted` (Source: Payments → Consumer: Booking, Notification)
- `InvoiceGenerated` (Source: Payments → Consumer: Notification)

## 6. Authentication & Authorization
Firebase Auth handles identity verification.
**Flow**: Firebase Auth → ID Token → `FirebaseAuthenticationFilter` → PostgreSQL user lookup → Spring Security RBAC.
- **Identity**: Authenticated by Firebase.
- **Authorization**: Dictated by PostgreSQL roles.
- **User Deactivation**: If `is_active=false` in PostgreSQL, backend requests are rejected immediately, regardless of Firebase token validity.

*Note on SafetyNet*: SafetyNet is deprecated. The project strictly uses the Play Integrity API (Firebase App Check V1) for attestation.

## 7. Tenant / Agency Model
Multi-agency model support.
- **Agency-Scoped Entities**: Employees, inventory, expenses, work orders, service visits, support tickets.
- **Global Entities**: Service catalog, global pricing rules.
- **Security Rule**: Strict boundary enforcement. No cross-agency resource access is permitted via ID manipulation in API requests.

## 8. Offline Synchronization (Technician App)
**Architecture**: Room DB → PendingOperation Queue → WorkManager → Spring Boot `/api/v1/dispatch/visits/sync`.
- **Fields**: `device_id`, `event_id` (UUID), `operation_id` (UUID), `local_sequence` (BIGINT), `client_created_at`, `server_received_at`, `payload` (JSONB), `payload_version` (INT), `retry_count`, `sync_status`.
- **Security & Idempotency**: NO cryptographic signing of offline payloads in V1.
  - Replaced by: Authenticated JWT + `device_id` + `operation_id` (idempotency key) + monotonic local sequence + server timestamps + server-side state validation + audit logging.

## 9. Payment Architecture
The client **never** declares payment success. Payment state is strictly updated via server-to-server Webhooks.
- Uses `payment_events` table for idempotency.
- Webhook updates payment state → Outbox event `PaymentCompleted` → Triggers `InvoiceGenerated`.

## 10. Inventory Concurrency
Uses PostgreSQL transactional deduction.
```text
BEGIN;
SELECT FOR UPDATE (lock row);
Validate qty >= deduction;
UPDATE quantity;
INSERT inventory_transaction;
INSERT service_material_usage;
COMMIT;
```
Enforced by `CHECK (current_quantity >= 0)`. Duplicate syncs handled by `operation_id` idempotency.

## 11. Booking Slot Concurrency
Handled via `availability_slots` table with `booked_count` and `capacity`.
- Transactional `SELECT FOR UPDATE` during booking confirmation.
- `UNIQUE` constraint prevents double-booking the same technician for the same slot.
- Fallback/Alternative: PostgreSQL advisory locks (`pg_try_advisory_xact_lock`).

## 12. File Storage
Managed via `file_metadata` table.
- **Schema**: `id`, `agency_id`, `entity_type`, `entity_id`, `file_purpose`, `storage_provider`, `storage_key`, `file_name`, `mime_type`, `file_size_bytes`, `checksum_sha256`, `uploaded_by`, `created_at`, `access_policy`.
- Presigned URLs are generated ONLY after verifying authorization in the backend.

## 13. Scheduling
- **Current**: Spring `@Scheduled` for AMC cron. Daily `01:00 UTC` job generates work orders for AMC visits due in 7 days.
- **Future**: Quartz for HA clustering and advanced scheduling.

## 14. Observability
- Metrics: Spring Actuator + Micrometer + Prometheus.
- Tracing: MDC correlation ID (`X-Correlation-ID`).
- Logging: Structured JSON logs via Logback.
- **Strict Rule**: NEVER log PII, authentication tokens, or raw payment data.

## 15. Deployment Model
- Local/Dev: Docker Compose (Postgres, Redis, RabbitMQ).
- Build: Multi-stage Dockerfile.
- Proxy: Nginx reverse proxy.
- CI/CD: GitHub Actions.
- Migrations: Flyway (runs before Spring Boot startup).

## 16. Implementation Status
Refer to the top of this document. Currently in the Documentation / Architecture Baseline phase.

## 17. Future Microservice Strategy
Modular Monolith is the architecture for V1.
- Future extraction candidates: Booking, Payment, Dispatch, Notification, Inventory, AMC.
- Extraction will only occur when justified by scale, team size, or reliability constraints.
- Transition mechanism: Strangler Fig Pattern.
