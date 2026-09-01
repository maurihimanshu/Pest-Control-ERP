# Backend Architecture Specification
## Spring Boot 3.x & Java 21 Modular Monolith

**Document Version:** 1.0.0  
**Framework:** Spring Boot 3.3.x  
**Language Runtime:** Java 21 LTS (OpenJDK / Eclipse Temurin)  
**Build Tool:** Apache Maven 3.9.x  
**Database:** PostgreSQL 16 with Spring Data JPA & Flyway  
**Messaging & Caching:** RabbitMQ 3.13 & Redis 7.2  
**Date:** September 2026  

---

## 1. Modular Monolith Design Philosophy

The backend application is structured as a **Single Deployable Spring Boot Modular Monolith**.

### Key Architectural Tenets:
1. **Logical Module Independence:** Code is organized by high-cohesion business domains (`bookings`, `dispatch`, `payments`, `inventory`, `amc`) rather than purely technical layers.
2. **Internal Communication via Services:** Modules communicate with each other through clean Java service interfaces or asynchronous domain events over RabbitMQ.
3. **No Circular Dependencies:** A strict dependency hierarchy is maintained (e.g., `bookings` depends on `pricing` and `customers`, but `customers` never depends on `bookings`).
4. **Microservices-Ready:** If a specific domain (such as `dispatch` or `payments`) requires independent deployment or high-throughput scaling in the future, its clear domain boundaries allow clean extraction without major refactoring.

---

## 2. Directory & Package Structure

The Maven codebase lives under `backend/` and follows standard Spring conventions:

```text
backend/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/com/pestcontrol/
    │   │   ├── Application.java               # Spring Boot main entrypoint
    │   │   │
    │   │   ├── common/                        # Cross-cutting foundational utilities
    │   │   │   ├── config/                    # Redis, RabbitMQ, Async, OpenAPI configs
    │   │   │   ├── exception/                 # Global error handler, standard error DTO
    │   │   │   ├── security/                  # Firebase Token Filter, UserPrincipal, RBAC
    │   │   │   ├── audit/                     # Spring Data JPA Auditing & MDC Logging
    │   │   │   └── utils/                     # DateUtils, IdGenerator, CurrencyUtils
    │   │   │
    │   │   └── modules/                       # Domain Business Modules
    │   │       ├── auth/                      # Firebase token verification & claims
    │   │       ├── users/                     # User entity, roles, status
    │   │       ├── customers/                 # Customer profiles, addresses
    │   │       ├── employees/                 # Technicians, skills, attendance
    │   │       ├── agencies/                  # Branch offices, franchises, commissions
    │   │       ├── services/                  # Service catalog, categories, packages
    │   │       ├── pricing/                   # Dynamic rate engine, coupons, taxes
    │   │       ├── bookings/                  # Booking commercial lifecycle
    │   │       ├── scheduling/                # Time slots, calendar availability
    │   │       ├── dispatch/                  # Work Orders, Service Visits, field sync
    │   │       ├── payments/                  # Payment gateway integrations & webhooks
    │   │       ├── invoices/                  # PDF invoice generation & numbering
    │   │       ├── expenses/                  # Operational expense logging & receipts
    │   │       ├── inventory/                 # Chemicals, batches, trunk stock, usage
    │   │       ├── amc/                       # Annual Maintenance Contracts & cron visits
    │   │       ├── notifications/             # FCM push, SMS, Email, WhatsApp dispatch
    │   │       ├── support/                   # Customer complaints & ticket workflows
    │   │       ├── reports/                   # Operational & financial analytics
    │   │       └── audit/                     # Immutable database audit trail
    │   │
    │   └── resources/
    │       ├── application.yml                # Base configuration
    │       ├── application-dev.yml            # Local development profile
    │       ├── application-prod.yml           # Production environment profile
    │       └── db/migration/                  # Flyway SQL migration scripts
    │           ├── V1__init_users_and_roles.sql
    │           ├── V2__init_services_and_pricing.sql
    │           ├── V3__init_bookings_and_dispatch.sql
    │           ├── V4__init_payments_and_invoices.sql
    │           ├── V5__init_inventory_and_chemicals.sql
    │           └── V6__init_amc_and_contracts.sql
    │
    └── test/                                  # Comprehensive Test Suite
        ├── java/com/pestcontrol/
        │   ├── modules/                       # Unit tests (Mockito / JUnit 5)
        │   └── integration/                   # Testcontainers (PostgreSQL, Redis, RabbitMQ)
        └── resources/
            └── application-test.yml
```

---

## 3. Standard Module Layering Pattern

Every module inside `com.pestcontrol.modules.<module_name>` implements a standardized 8-tier internal structure:

```text
com.pestcontrol.modules.bookings/
├── controller/        # REST Controllers (@RestController) exposing /api/v1/bookings
├── service/           # Business logic interfaces & @Service implementations
├── repository/        # Spring Data JPA interfaces (@Repository)
├── entity/            # JPA Entities (@Entity, @Table) mapping PostgreSQL tables
├── dto/               # Request & Response Data Transfer Objects with validation annotations
│   ├── request/       # CreateBookingRequest, RescheduleBookingRequest
│   └── response/      # BookingResponse, BookingSummaryResponse
├── mapper/            # MapStruct mappers (Entity <-> DTO)
├── exception/         # Domain-specific exceptions (BookingNotFoundException, SlotUnavailableException)
└── validation/        # Custom bean validation constraints (@ValidBookingSchedule)
```

---

## 4. Cross-Cutting Infrastructure Components

### 4.1 Security & Authentication Filter
1. **Firebase Admin SDK:** Validates incoming Bearer JWT tokens against Google Firebase public keys.
2. **`FirebaseAuthenticationFilter`:** Intercepts HTTP requests, extracts the Firebase `uid` and email, retrieves the local `User` entity from PostgreSQL (or creates one on first login), and sets the `SecurityContextHolder`.
3. **Method-Level Security:** Enforced via Spring Security `@PreAuthorize("hasRole('ADMIN')")` or `@PreAuthorize("hasAuthority('BOOKING_READ')")`.

### 4.2 Database Migrations (Flyway)
* All DDL changes are strictly version-controlled via SQL files in `src/main/resources/db/migration/`.
* Hibernate `ddl-auto` is set to `validate` in all environments to prevent automated table alterations.
* Migrations run automatically on application startup before the Spring context is initialized.

### 4.3 Redis Caching & Distributed Locking
* **Spring Cache Abstraction (`@Cacheable`):**
  * `services`: Cached with 24-hour TTL; evicted upon admin catalog updates.
  * `pricing_rules`: Cached with 1-hour TTL.
  * `technician_skills`: Cached with 12-hour TTL.
* **Distributed Locking (Redisson / Redis Locks):**
  * Slot reservation and technician assignment use a Redis distributed lock (`lock:slot:{technicianId}:{date}:{slot}`) to prevent double-booking race conditions during simultaneous checkouts.

### 4.4 RabbitMQ Messaging & Event-Driven Decoupling
* **Exchange Configuration:** `TopicExchange` named `erp.events.topic`.
* **Standard Domain Events:**
  * `booking.created`
  * `booking.confirmed`
  * `workorder.assigned`
  * `visit.completed`
  * `payment.success`
  * `invoice.generated`
  * `inventory.low_stock`
* **Reliability Features:**
  * Manual ACK mode enabled (`AcknowledgeMode.MANUAL`).
  * Dead Letter Exchange (`erp.dlx.topic`) for failed events after 3 exponential backoff retries.

---

## 5. Observability & Production Monitoring

### 5.1 Spring Boot Actuator & Micrometer
* Health check endpoint: `/actuator/health` (probes for PostgreSQL, Redis, RabbitMQ, and Disk space).
* Metrics endpoint: `/actuator/prometheus` scraped by Prometheus.

### 5.2 Key Monitored Application Metrics:
* `erp.bookings.created.count`: Total booking requests created.
* `erp.payments.failed.count`: Payment gateway rejections/failures.
* `erp.technician.offline_sync.duration`: Milliseconds required to process an offline field visit sync.
* `erp.rabbitmq.queue.depth`: Unprocessed messages waiting in notification and invoice queues.

### 5.3 Structured Logging & Request Tracing (MDC)
* Every incoming request receives a unique `traceId` (or extracts `X-Correlation-ID`).
* Log format is structured JSON in production containing: `timestamp`, `level`, `traceId`, `userId`, `thread`, `logger`, `message`.

---

## 6. Microservices Evolution Strategy

```text
                         [ STAGE 1: Current Architecture ]
                        ┌─────────────────────────────────┐
                        │ Spring Boot Modular Monolith    │
                        │  (Single JVM / Single Maven App)│
                        └────────────────┬────────────────┘
                                         │
                                         ▼ (Driven by Scale & Team Growth)
                         [ STAGE 2: Future Target ]
                        ┌─────────────────────────────────┐
                        │      Spring Cloud Gateway       │
                        └────────┬───────┬───────┬────────┘
                                 │       │       │
             ┌───────────────────┘       │       └───────────────────┐
             ▼                           ▼                           ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│     Booking Service     │ │    Dispatch Service     │ │    Financial Service    │
│  (Customers, Bookings)  │ │(Technicians, Field Sync)│ │  (Payments, Invoicing)  │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
```

> **Guiding Principle:** Do not extract microservices until a clear business driver (independent deployment velocity, specialized compliance boundaries, or 10x throughput differentials) justifies the operational cost.

---

*Governed by enterprise software engineering and Spring Boot architectural best practices.*
