# System Architecture Specification
## Pest Control Enterprise Resource Planning (ERP) Platform

**Document Version:** 2.0.0  
**Backend Runtime:** Java 21 + Spring Boot 3.3.x (Maven)  
**Primary Database:** PostgreSQL 16  
**Cache & Locks:** Redis 7.x  
**Message Broker:** RabbitMQ 3.13.x  
**Supporting Cloud:** Firebase Auth & FCM, Provider-Neutral Object Storage  
**Date:** September 2026  

---

## 1. Architectural Vision & Guiding Principles

The Pest Control ERP is an enterprise-grade field service management and operations platform. It transitions from prototype serverless concepts to a robust, scalable **Spring Boot Modular Monolith** serving native mobile clients and a React web dashboard.

### Core Architectural Principles:
1. **Modular Monolith First:** Maintain a single deployable Spring Boot application with strict domain-driven boundaries between internal modules (`bookings`, `dispatch`, `payments`, `inventory`, etc.). Microservices are avoided in early stages to minimize operational overhead.
2. **PostgreSQL as System-of-Record:** All relational, financial, transactional, and audit data reside in PostgreSQL with full ACID guarantees.
3. **Decoupled Asynchronous Processing:** RabbitMQ decouples non-blocking domain events (push notifications, PDF generation, audit logs, email alerts) from transactional request threads.
4. **Offline-First Field Mobility:** Field technicians operate uninterrupted without connectivity using local SQLite (Room DB) and synchronize via idempotent REST APIs.
5. **Zero-Trust Backend Authorization:** Client applications are untrusted presentation layers. Spring Security enforces role-based access control (RBAC) on every protected API endpoint after verifying Firebase-issued ID tokens.

---

## 2. High-Level System Architecture Diagram

```text
                                 ┌─────────────────────────────────┐
                                 │       React Admin Web App       │
                                 │     (React 18 + TypeScript)     │
                                 └────────────────┬────────────────┘
                                                  │ HTTPS / REST
                                                  ▼
 ┌────────────────────────┐             ┌───────────────────┐             ┌────────────────────────┐
 │  Customer Android App  │             │   Load Balancer   │             │ Technician Android App │
 │ (Java 21 + Room Cache) │────────────►│  (Nginx / Traefik)│◄────────────│ (Java 21 + Room Cache) │
 └────────────────────────┘ HTTPS/REST  └─────────┬─────────┘ HTTPS/REST  └────────────────────────┘
                                                  │
                                                  ▼
                        ┌──────────────────────────────────────────────────┐
                        │        Spring Boot Core Modular Monolith         │
                        │           (Java 21 / Maven / Spring 3.x)         │
                        ├──────────────────────────────────────────────────┤
                        │ • Security & Firebase Token Filter               │
                        │ • REST API Controllers (/api/v1/*)               │
                        │ • Domain Services & Business Rules Engine        │
                        │ • JPA / Hibernate Repositories                   │
                        │ • RabbitMQ Event Publishers & Consumers          │
                        │ • Spring Actuator & Micrometer Observability     │
                        └─────────┬───────────────┬───────────────┬────────┘
                                  │               │               │
                 ┌────────────────┴────┐   ┌──────┴──────┐  ┌─────┴──────────────┐
                 ▼                     ▼   ▼             ▼  ▼                    ▼
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │    PostgreSQL    │  │      Redis       │  │     RabbitMQ     │  │  Object Storage  │
        │ Primary Relational│  │ Cache, Locks &   │  │ Async Events &   │  │ S3 / GCS / Cloud │
        │    Database      │  │  Rate Limiting   │  │ Task Decoupling  │  │ (PDFs, Media)    │
        └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
                                       │                     │
                                       ▼                     ▼
                        ┌──────────────────────────────────────────────────┐
                        │            External Supporting Services          │
                        ├──────────────────────────────────────────────────┤
                        │ • Firebase Authentication (Identity Provider)    │
                        │ • Firebase Cloud Messaging (FCM Push Alerts)     │
                        │ • Payment Gateway (Razorpay / Stripe)            │
                        │ • SMS / WhatsApp Gateway (MSG91 / Twilio)        │
                        │ • Google Maps Platform (Geocoding & Places)      │
                        └──────────────────────────────────────────────────┘
```

---

## 3. Technology Stack Specification

| Tier / Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | Spring Boot | 3.3.x | Enterprise application framework |
| **Language Runtime** | Java (OpenJDK) | 21 LTS | High-performance virtual threads, pattern matching |
| **Build System** | Apache Maven | 3.9.x | Dependency management and build lifecycle |
| **Primary Database** | PostgreSQL | 16.x | Relational ACID database, JSONB for dynamic metadata |
| **Database Migrations**| Flyway | 10.x | Version-controlled, reproducible schema migrations |
| **ORM / Data Access** | Spring Data JPA / Hibernate | 6.5.x | Object-relational mapping, domain repositories |
| **In-Memory Cache** | Redis | 7.2.x | Reference data caching, distributed locks, rate limiting |
| **Message Broker** | RabbitMQ | 3.13.x | Reliable asynchronous event queuing and pub/sub |
| **API Documentation** | Springdoc OpenAPI (Swagger UI) | 2.5.x | Interactive, auto-generated REST API specification |
| **Security Framework** | Spring Security + Firebase Admin | 6.3.x | JWT token validation, custom RBAC authorization |
| **Customer Mobile App**| Android Native (Java 21) | SDK 34/35 | Customer booking, slot selection, payments, tracking |
| **Technician Mobile** | Android Native (Java 21) | SDK 34/35 | Offline-first field execution, Room DB, CameraX, WorkManager |
| **Admin Web ERP** | React + TypeScript | 18.x / 5.x | Dispatch board, financial accounting, inventory, reports |
| **Object Storage** | S3 / GCS / Cloud Storage | API v2 | Provider-neutral storage for photos, invoices, attachments |
| **Identity Provider** | Firebase Authentication | v9 SDK | Customer OTP, Employee PIN/Email, Admin credentials |
| **Push Alerts** | Firebase Cloud Messaging (FCM) | HTTP v1 API | Cross-platform real-time push notifications |

---

## 4. C4 Container & Architectural Layers

### 4.1 Client Presentation Layer
* **Customer Android App:** Communicates with Spring Boot via `/api/v1/*` HTTPS endpoints. Uses Firebase Auth SDK to obtain ID tokens and sends them in `Authorization: Bearer <token>` headers.
* **Technician Android App:** Contains an internal SQLite (Room DB) action queue. Background sync uses Android `WorkManager` to push completed service visits to `/api/v1/dispatch/visits/sync` upon network recovery.
* **Admin Web Dashboard:** Single Page Application (SPA) built with React, Vite, and TypeScript. Consumes REST APIs with server-side pagination, sorting, and filtering.

### 4.2 API & Ingress Layer
* **Reverse Proxy / Load Balancer:** Nginx handles TLS 1.3 termination, HTTP/2 multiplexing, static asset caching, and request forwarding to backend application containers.
* **Spring Security Gateway Filter:** Intercepts every incoming request, validates the Firebase JWT signature, extracts `uid` and custom claims, looks up or syncs the internal `User` entity, and sets the `SecurityContext`.

### 4.3 Modular Core Business Layer
Logical domain modules live within the same Spring Boot monolith:
* `auth` & `users`: Identity synchronization, profile management, role assignment.
* `customers` & `employees`: Customer address books, technician skills, availability calendars.
* `services` & `pricing`: Hierarchical service catalog, dynamic rate engine (sq. ft., room type, surcharges).
* `bookings`, `scheduling` & `dispatch`: 3-tier lifecycle management (Booking $\rightarrow$ Work Order $\rightarrow$ Service Visit).
* `payments` & `invoices`: Payment initiation, webhook signature verification, atomic PDF invoice generation.
* `inventory`: Chemical products, batches, warehouse locations, technician trunk stock, field consumption logs.
* `amc`: Annual Maintenance Contracts, automated scheduled visit generation via Spring Scheduler.
* `notifications`: Multi-channel dispatch (FCM, SMS, Email, WhatsApp).
* `reports` & `audit`: Financial reconciliations, operational metrics, immutable event audit logs.

### 4.4 Persistence & Messaging Layer
* **PostgreSQL:** System-of-record storing all relational entities, foreign keys, and transaction history.
* **Redis:** Caches static service rates, technician live availability slots, and manages Redlock distributed locks for slot booking.
* **RabbitMQ:** Exchanges route domain events (`booking.created`, `visit.completed`, `payment.success`) to designated queues.
* **Object Storage:** Stores raw binaries (before/after inspection photos, customer signatures, generated PDF invoices) with signed URL access.

---

## 5. Domain Boundary Decomposition (3-Tier Booking Model)

To support complex field operations, multiple visits, follow-up treatments, warranty visits, and AMC contracts, the system decouples the customer request from physical field execution:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        1. Commercial Request                            │
│                              BOOKING                                    │
│  • Customer Details, Target Address, Selected Services, Pricing Model  │
│  • Commercial Status (PENDING, CONFIRMED, CANCELLED, CLOSED)            │
│  • Billing & Payment Status (PENDING, PAID, REFUNDED)                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ 1 : N
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       2. Operational Assignment                         │
│                             WORK ORDER                                  │
│  • Operational Scope (Initial Treatment, Warranty Follow-Up, AMC Run)  │
│  • Assigned Branch/Agency, Dispatch Priority, SLA Due Date             │
│  • Operational Status (UNASSIGNED, ASSIGNED, IN_PROGRESS, COMPLETED)   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ 1 : N
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        3. Physical Execution                            │
│                            SERVICE VISIT                                │
│  • Primary Field Technician, Scheduled Date & Time Slot                 │
│  • Visit Status (SCHEDULED, EN_ROUTE, ARRIVED, IN_PROGRESS, COMPLETED)  │
│  • Field Evidence (Chemicals Used, Batch Nos, Photos, Signature)       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Asynchronous Event Pipeline (RabbitMQ Integration)

When critical state mutations occur in Spring Boot, transactional events are published to RabbitMQ topic exchanges:

```text
[ Spring Boot DB Transaction Commits ]
                  │
                  ▼
   (Spring Transactional Event Publisher)
                  │
                  ▼
         [ RabbitMQ Exchange: erp.events ]
                  │
        ┌─────────┼─────────┬─────────┐
        │ Routing │ Routing │ Routing │
        ▼ Keys    ▼ Keys    ▼ Keys    ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ q.notification│ │  q.invoicing  │ │ q.inventory   │
├───────────────┤ ├───────────────┤ ├───────────────┤
│ • Send FCM    │ │ • Build PDF   │ │ • Deduct stock│
│ • Send SMS/OTP│ │ • Upload S3   │ │ • Check batch │
│ • Send Email  │ │ • Notify user │ │ • Low alert   │
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## 7. Architecture Rationale: Modular Monolith vs. Distributed Serverless

| Dimension | Distributed Serverless Prototype (Deprecated) | Enterprise Spring Boot Architecture (Approved) |
| :--- | :--- | :--- |
| **Backend Engine** | Distributed Cloud Triggers | Java 21 + Spring Boot 3.x Modular Monolith |
| **Data Consistency** | Eventual consistency (NoSQL) | Strong ACID transactions (PostgreSQL 16) |
| **Relational Integrity**| Manual document references | Foreign keys, constraints, cascade rules |
| **Business Logic** | Scattered serverless functions | Co-located in Spring Domain Services |
| **Async Events** | Cloud messaging pipelines | RabbitMQ Topics & Queues with Dead Letter Exchanges |
| **Local Development** | Cloud Emulators | Standard Docker Compose (PostgreSQL, Redis, RabbitMQ) |
| **Testing Suite** | Emulator integration scripts | JUnit 5 + Mockito + Testcontainers |

---

*This architecture document governs all module designs, database schemas, and API contracts.*
