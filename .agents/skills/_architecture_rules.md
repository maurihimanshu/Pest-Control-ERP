---
name: architecture-rules
description: Non-negotiable architecture rules every agent MUST read and follow before taking any action on the Pest Control ERP project.
category: architecture
triggers:
  - before coding
  - before editing any file
  - architecture constraints
  - what architecture should I use
  - read rules first
inputs: []
outputs:
  - enforced architecture compliance
dependencies: []
related_skills:
  - architecture/architecture-discovery
  - architecture/legacy-architecture-audit
  - architecture/impact-analysis
---

# ⚠️ Architecture Rules — Read Before Any Action

> **MANDATORY**: Every agent must read this document before modifying, creating, or reviewing any file in this repository.

---

## 1. Approved Architecture — Single Source of Truth

```
Customer Android ──────┐
                       │
Technician Android ────┼──► Spring Boot REST API (Java 21 + Maven + Modular Monolith)
                       │         │
Admin React ───────────┘         ├── PostgreSQL 16  ← System-of-Record
                                 ├── Redis           ← Cache / Locks ONLY
                                 ├── RabbitMQ        ← Async Events ONLY
                                 └── Object Storage  ← Photos / PDFs / Signatures

Supporting External Services (NOT core ERP):
  ├── Firebase Authentication  ← Identity provider only
  ├── Firebase Cloud Messaging ← Push notifications only
  ├── Google Maps              ← Geocoding / places
  ├── SMS Provider             ← Transactional OTP / alerts
  ├── Email Provider           ← Transactional email
  └── Payment Gateway          ← Razorpay / Stripe webhooks
```

---

## 2. Backend Rules

| Rule | Detail |
|:---|:---|
| **Language** | Java 21 LTS |
| **Framework** | Spring Boot 3.x |
| **Build** | Maven |
| **Pattern** | Modular Monolith — one deployable JAR, 18 domain modules |
| **No microservices in V1** | Only extract modules when justified by scale/ownership/reliability |
| **REST API prefix** | `/api/v1/*` for all endpoints |
| **Web layer** | Spring MVC (`@RestController`) |
| **Security** | Spring Security 6.x — stateless JWT filter chain |
| **ORM** | Spring Data JPA + Hibernate |
| **DB migrations** | Flyway — versioned SQL `V{n}__{description}.sql` |
| **Bean Validation** | Jakarta Bean Validation on all request DTOs |
| **API docs** | Springdoc OpenAPI (`/api-docs`, `/swagger-ui`) |
| **PDF generation** | OpenPDF inside `InvoiceService` |
| **Scheduling** | Spring `@Scheduled` — Quartz only if distributed scheduling required |

### 18 Domain Modules

```
com.pestcontrol.modules.
├── auth          ├── scheduling    ├── expenses
├── users         ├── dispatch      ├── inventory
├── customers     ├── payments      ├── amc
├── employees     ├── invoices      ├── notifications
├── agencies      ├── support       ├── reports
├── services      ├── pricing       └── audit
└── bookings
```

---

## 3. Database Rules

| Rule | Detail |
|:---|:---|
| **System-of-Record** | PostgreSQL 16 — ALL ERP data lives here |
| **Primary keys** | `UUID` via `gen_random_uuid()` |
| **Timestamps** | `created_at TIMESTAMPTZ DEFAULT NOW()`, `updated_at TIMESTAMPTZ` |
| **Naming** | `snake_case` for all tables and columns |
| **Invoice numbering** | PostgreSQL `SEQUENCE` — format `INV-YYYY-NNNNN` |
| **Audit logging** | Append-only `audit_logs` table — NEVER update or delete rows |
| **Migrations** | Every schema change MUST have a Flyway migration script |
| **No app-side counters** | Use PostgreSQL sequences, not Redis or in-memory counters |

### FORBIDDEN as ERP database:
- ❌ Firestore / Cloud Firestore
- ❌ Firebase Realtime Database
- ❌ Redis (cache only)
- ❌ In-memory stores

---

## 4. Firebase Rules — Supporting Services Only

| Firebase Feature | Allowed Use | Forbidden Use |
|:---|:---|:---|
| **Firebase Authentication** | Issue ID tokens for Customer/Technician/Admin | Store ERP data |
| **Firebase Cloud Messaging** | Push notification delivery | Business logic |
| **Firebase Storage** | Object storage provider (if selected) | ERP database |
| **Firestore** | ❌ NOT permitted for any ERP use | — |
| **Cloud Functions** | ❌ NOT permitted as backend | — |
| **Cloud Scheduler** | ❌ NOT permitted — use Spring `@Scheduled` | — |

### Firebase Authentication Flow (CORRECT)

```
Client App
  ↓ Signs in with Firebase Auth
  ↓ Receives Firebase ID Token
  ↓ Sends: Authorization: Bearer <id-token>
Spring Boot FirebaseAuthenticationFilter
  ↓ Verifies token signature via Firebase Admin SDK
  ↓ Extracts UID and custom claims
  ↓ Loads user record from PostgreSQL (roles, status)
  ↓ Creates Spring Security Authentication object
Spring Security RBAC
  ↓ Evaluates @PreAuthorize SpEL expressions
  ↓ Enforces resource-level ownership checks
```

---

## 5. Domain Model Rules — NEVER Collapse These Three Entities

### Booking (Commercial Request)
- Customer's service request with pricing, address, schedule
- **Status**: `PENDING` → `CONFIRMED` → `ASSIGNED` → `IN_PROGRESS` → `COMPLETED` → `CANCELLED` | `RESCHEDULED` | `CLOSED`

### Work Order (Operational Dispatch)
- Created from a Booking; represents the operational job dispatched to a technician
- Contains: booking_id FK, assigned employee, agency, operational status
- **Status**: `ASSIGNED` → `ACCEPTED` | `REJECTED` → `ON_THE_WAY` → `ARRIVED` → `STARTED` → `COMPLETED`

### Service Visit (Physical Field Execution)
- Belongs to a Work Order; represents what physically happened on-site
- Contains: arrival_time, start_time, end_time, checklist JSONB, chemicals, photos[], GPS, signature, notes
- Supports: rescheduling, warranty visits, AMC recurring visits, multi-technician

### Payment State Machine
- `PENDING` → `AUTHORIZED` → `PAID` | `PARTIAL` | `FAILED`
- `PAID` → `REFUNDED` | `PARTIALLY_REFUNDED`

---

## 6. Redis Rules

| Allowed | Forbidden |
|:---|:---|
| Caching service catalog, pricing rules | Storing booking or payment state |
| Distributed slot locking (Redlock) | Storing user records |
| Rate limiting (sliding window counter) | Being the system-of-record for anything |
| Temporary OTP/session state | Replacing PostgreSQL transactions |

- Cache key convention: `pestcontrol:{module}:{entity}:{id}`
- All cached data MUST also exist in PostgreSQL
- TTL MUST be set on every Redis key

---

## 7. RabbitMQ Rules

| Allowed | Forbidden |
|:---|:---|
| Decoupled async domain events | Synchronous request-response (use REST) |
| Notification dispatch (FCM/SMS/Email) | Storing business state |
| Invoice generation trigger | Replacing PostgreSQL ACID transactions |
| Inventory deduction trigger | Ordering without outbox pattern |

### Standard Domain Events

```
BookingCreated      WorkOrderCreated      PaymentCompleted
BookingConfirmed    TechnicianAssigned    InvoiceGenerated
BookingCancelled    TechnicianAccepted    NotificationRequested
                    ServiceStarted        AMCVisitGenerated
                    ServiceCompleted
```

- Use **Outbox Pattern** for reliable event publication
- All consumers MUST be **idempotent** — duplicate events must be harmless
- Every queue MUST have a **Dead Letter Exchange (DLX)** configured
- Event format: `{ eventId, eventType, occurredAt, version, payload }`

---

## 8. Security Rules

1. **Backend is authoritative** — never trust client for price, payment state, booking state, or permissions
2. **RBAC server-side** — 7 roles: `SUPER_ADMIN`, `ADMIN`, `DISPATCHER`, `AGENCY_MANAGER`, `ACCOUNTANT`, `TECHNICIAN`, `CUSTOMER`
3. **Resource ownership** — technician can only access their own jobs; customer can only access their own bookings
4. **Payment webhooks** — always validate HMAC-SHA256 signature before processing
5. **No PII in logs** — never log tokens, passwords, card numbers, OTPs, or personal data
6. **HTTPS only** — TLS enforced at load balancer
7. **Idempotency** — all retryable mutating operations MUST support `Idempotency-Key` header

---

## 9. Technician Offline Rules

```
Technician Android (offline-capable)
  └── Room SQLite + SQLCipher encryption
  └── PendingOperation queue table:
        (operation_id UUID, idempotency_key, type, payload JSON,
         status, retry_count, client_timestamp, sync_status)
  └── CameraX → WebP compression < 500 KB before upload
  └── WorkManager SyncWorker (exponential backoff, network constraint)
  └── POST /api/v1/dispatch/visits/sync → Spring Boot → PostgreSQL
```

- **Conflict rule**: Physical field completion OVERRIDES administrative online cancellation — logged in audit_logs
- Backend NEVER blindly overwrites server state with stale client data
- Each offline operation has a unique `operation_id` and `idempotency_key`

---

## 10. Agent Safety Rules

| Rule | Requirement |
|:---|:---|
| **Inspect before editing** | Read the target file and related code before modifying |
| **Minimal scope** | Only change what the task requires — leave unrelated code untouched |
| **Preserve behavior** | Never change existing behavior unless explicitly required |
| **Tests mandatory** | Every business logic change requires an automated test |
| **No fake implementations** | No hardcoded responses or mock payment success in production code |
| **No architecture drift** | Never introduce Firestore, Cloud Functions, or microservices |
| **Audit trail** | Financial, inventory, security, and status changes must be logged |
| **Documentation sync** | After any implementation, verify docs still match the code |

---

## 11. Forbidden Patterns — Flag Immediately

```
❌ FirebaseFirestore.getInstance()
❌ db.collection("bookings")
❌ functions.https.onCall(...)
❌ functions.https.onRequest(...)
❌ admin.firestore().doc(...)
❌ Cloud Scheduler (non-Spring scheduling)
❌ Pub/Sub topic subscription for core ERP events
❌ redisClient.set("payment:123", paymentState)   // business state in Redis
❌ client.send({ paymentSuccess: true })           // client claiming payment success
❌ new AtomicInteger() for invoice numbering       // use PostgreSQL SEQUENCE
❌ @Service class communicating directly with another module's @Repository
```
