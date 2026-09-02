# 🐜 Enterprise Pest Control Management & ERP Platform
### Commercial & Technical Project Proposal

**Repository:** `https://github.com/maurihimanshu/Pest-Control-ERP`  
**Backend Architecture:** Java 21 + Spring Boot 3.3.x (Modular Monolith)  
**Primary Database:** PostgreSQL 16  
**Cache & Message Broker:** Redis 7.2 & RabbitMQ 3.13  
**Client Applications:** Customer Android (Java 21), Technician Android (Java 21, Offline-First), Admin Web (React 18 + TypeScript)  

---

## 📌 Executive Summary

Modern pest control operations require seamless orchestration between customer acquisition, field technician dispatching, on-site service verification, inventory control, and financial reporting. 

This repository houses the complete engineering and product documentation for the **Pest Control Enterprise Resource Planning (ERP) Platform**. The system unifies customer self-service, offline-capable field workforce management, and executive operational control into a robust, high-performance **Spring Boot Modular Monolith** backed by PostgreSQL, Redis, and RabbitMQ.

```text
                         ┌──────────────────────────┐
                         │      React Admin Web     │
                         │   React 18 + TypeScript  │
                         └────────────┬─────────────┘
                                      │ HTTPS / REST
                         ┌────────────▼─────────────┐
                         │       REST API            │
                         │      Spring Boot          │
                         │        Java 21           │
                         └────────────┬─────────────┘
                                      │
        ┌─────────────────────────────┼──────────────────────────────┐
        │                             │                              │
        ▼                             ▼                              ▼
 Customer Android              Technician Android              Admin Web
 Java 21                       Java 21                         React/TS
 Firebase Auth                 Firebase Auth                   Firebase Auth
 REST API                      REST API                        REST API
 Room Database                 Room Database                   Ant Design
 WorkManager                   WorkManager                     Recharts
 CameraX                       CameraX                         Vite
        │                             │                              │
        └─────────────────────────────┼──────────────────────────────┘
                                      │
                             ┌────────▼─────────┐
                             │   Spring Boot    │
                             │ Modular Monolith │
                             └────────┬─────────┘
                                      │
                    ┌─────────────────┼──────────────────┐
                    ▼                 ▼                  ▼
               PostgreSQL          Redis             RabbitMQ
               Primary DB          Cache             Async Events
                    │
                    ▼
              Object Storage
          Photos / Documents / PDFs
```

---

## 📂 Comprehensive Documentation Suite (`docs/`)

All detailed specifications, architecture designs, database DDL schemas, API contracts, offline sync protocols, and cost models are available in the dedicated documentation suite:

| Document | Description | Direct Link |
| :--- | :--- | :--- |
| 🏛️ **Architecture (Canonical)** | Primary architectural reference — all modules, boundaries, decisions. | [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) |
| 📦 **Module Catalog (Canonical)** | Master 18-module taxonomy, boundaries, owned tables, public APIs & event contracts. | [`docs/MODULE_CATALOG.md`](./docs/MODULE_CATALOG.md) |
| 🗂️ **Domain Model (Canonical)** | Entities, aggregates, state machines, invariants, business rules. | [`docs/DOMAIN_MODEL.md`](./docs/DOMAIN_MODEL.md) |
| 🔐 **RBAC & Permissions** | Single source of truth for all roles and permissions. | [`docs/RBAC_AND_PERMISSIONS.md`](./docs/RBAC_AND_PERMISSIONS.md) |
| ⚛️ **Concurrency & Idempotency** | Slot locking, inventory, payment webhook, offline sync, outbox. | [`docs/CONCURRENCY_AND_IDEMPOTENCY.md`](./docs/CONCURRENCY_AND_IDEMPOTENCY.md) |
| 📋 **Architecture Decisions** | Formal ADRs for major architectural decisions. | [`docs/adr/`](./docs/adr/) |
| 📋 **Software Requirements Specification (SRS)** | Complete module-by-module functional requirements, user roles, 3-tier domain model, and 3-release scope. | [**`docs/SOFTWARE_REQUIREMENTS_SPECIFICATION.md`**](./docs/SOFTWARE_REQUIREMENTS_SPECIFICATION.md) |
| 🏛️ **System Architecture** | High-level C4 container architecture, modular monolith design, technology matrix, and decoupled event pipelines. | [**`docs/SYSTEM_ARCHITECTURE.md`**](./docs/SYSTEM_ARCHITECTURE.md) |
| ⚙️ **Backend Architecture** | Spring Boot 3.3, Java 21, Maven package structure, Spring Security filter, Flyway migrations, Redis, and RabbitMQ. | [**`docs/BACKEND_ARCHITECTURE.md`**](./docs/BACKEND_ARCHITECTURE.md) |
| 🗄️ **Database Design & Schema** | PostgreSQL 16 DDL tables, foreign keys, indexes, 3-tier booking schema, inventory tables, and audit logs. | [**`docs/DATABASE_DESIGN.md`**](./docs/DATABASE_DESIGN.md) |
| 🌐 **REST API Specification** | OpenAPI / Springdoc specification, standard response envelopes, paginated queries, and `/api/v1/*` contracts. | [**`docs/API_SPECIFICATION.md`**](./docs/API_SPECIFICATION.md) |
| 🔐 **Authentication & Authorization** | Firebase ID token verification, Spring Security filter pipeline, RBAC matrix, and SpEL method security. | [**`docs/AUTHENTICATION_AND_AUTHORIZATION.md`**](./docs/AUTHENTICATION_AND_AUTHORIZATION.md) |
| 🔄 **Booking State Machine** | Decoupled state machines for Commercial Bookings, Work Orders, Service Visits, and Payments. | [**`docs/BOOKING_STATE_MACHINE.md`**](./docs/BOOKING_STATE_MACHINE.md) |
| 📶 **Offline-First Synchronization** | Android Room SQLite action queue, WorkManager sync, CameraX WebP compression, and conflict resolution rules. | [**`docs/OFFLINE_SYNC.md`**](./docs/OFFLINE_SYNC.md) |
| 💳 **Payment & Invoicing** | Gateway webhooks (Razorpay/Stripe), HMAC verification, COD field reconciliation, and automated PDF invoicing. | [**`docs/PAYMENT_ARCHITECTURE.md`**](./docs/PAYMENT_ARCHITECTURE.md) |
| 🔔 **Notification Architecture** | Multi-channel notification pipeline (FCM Push, Transactional SMS, Thymeleaf HTML Emails, WhatsApp). | [**`docs/NOTIFICATION_ARCHITECTURE.md`**](./docs/NOTIFICATION_ARCHITECTURE.md) |
| 🧪 **Inventory & Chemical Tracking** | Chemical product catalog, batch FIFO expiry tracking, multi-tier warehouse allocation, and COGS accounting. | [**`docs/INVENTORY_AND_CHEMICALS.md`**](./docs/INVENTORY_AND_CHEMICALS.md) |
| 📅 **AMC & Recurring Services** | Annual Maintenance Contract lifecycle, automated daily Spring Scheduler cron visit generation, and renewals. | [**`docs/AMC_ARCHITECTURE.md`**](./docs/AMC_ARCHITECTURE.md) |
| 📊 **Reporting & Analytics** | PostgreSQL operational analytics, pre-aggregated daily rollup tables, executive KPIs, and async CSV/Excel exports. | [**`docs/REPORTING.md`**](./docs/REPORTING.md) |
| 🛡️ **Security Policy & Standards** | Zero-trust architecture, encryption in transit/rest, offline data security, anti-tampering, and incident SLAs. | [**`SECURITY.md`**](./SECURITY.md) |
| 🧪 **Testing Strategy** | Quality assurance pyramid, JUnit 5, Mockito, Testcontainers (Postgres/Redis/RabbitMQ), and Android Room tests. | [**`docs/TESTING_STRATEGY.md`**](./docs/TESTING_STRATEGY.md) |
| 🚀 **Deployment Architecture** | Docker multi-stage builds, Nginx load balancing, production container topology, and GitHub Actions CI/CD. | [**`docs/DEPLOYMENT_ARCHITECTURE.md`**](./docs/DEPLOYMENT_ARCHITECTURE.md) |
| ⏱️ **Project Estimation & Resource Plan**| WBS effort estimates, 3-release sprint roadmap, team composition, skill sets, and development budget. | [**`docs/PROJECT_ESTIMATION_AND_RESOURCE_PLAN.md`**](./docs/PROJECT_ESTIMATION_AND_RESOURCE_PLAN.md) |
| ☁️ **Infrastructure & Operating Costs** | Cloud compute VPS, Managed PostgreSQL, Redis, RabbitMQ, Object Storage, Maps API, and SMS operating costs. | [**`docs/INFRASTRUCTURE_AND_OPERATING_COSTS.md`**](./docs/INFRASTRUCTURE_AND_OPERATING_COSTS.md) |
| 🤝 **Contributor Guide** | Developer local setup, Git Flow branching, Java 21 / React TS coding standards, and PR requirements. | [**`CONTRIBUTING.md`**](./CONTRIBUTING.md) |
| 📜 **Commercial License** | Proprietary and confidential enterprise software license terms and rights reservation. | [**`LICENSE`**](./LICENSE) |
| 📜 **Code of Conduct** | Community pledge, inclusive professional standards, and enforcement guidelines. | [**`CODE_OF_CONDUCT.md`**](./CODE_OF_CONDUCT.md) |

---

## 🛠️ Technology Stack & Standards

| Layer | Technology | Key Capabilities |
| :--- | :--- | :--- |
| **Backend Core** | Java 21 LTS + Spring Boot 3.3 (Maven) | Modular Monolith, Virtual Threads, Spring Security, Spring Data JPA, Hibernate |
| **Primary Database** | PostgreSQL 16 | ACID Relational Store, Flyway migrations, JSONB audit logs |
| **In-Memory Cache** | Redis 7.2 | Reference data caching, distributed Redlock for slot bookings |
| **Message Broker** | RabbitMQ 3.13 | Asynchronous decoupled event routing (Notifications, Invoicing, Inventory) |
| **Customer App** | Native Android (Java 21) | Android Jetpack, MVVM, Retrofit, Google Maps SDK, OTP Autofill |
| **Technician App** | Native Android (Java 21) | SQLite Room DB + SQLCipher, `WorkManager`, CameraX, Offline Transaction Queue |
| **Admin Web ERP** | React 18 + TypeScript | Vite, TailwindCSS, Ant Design, Recharts, Responsive Grid Layout |
| **Object Storage** | S3-Compatible / GCS / Cloud Storage | Provider-neutral binary store for photos, signatures, and PDF invoices |
| **Identity Provider** | Firebase Authentication | Phone OTP, Employee PIN, Admin credentials $\rightarrow$ Spring Security Token Filter |
| **Push Alerts** | Firebase Cloud Messaging (FCM) | HTTP v1 topic-based multicast alerts |

---

## 🗓️ Phased Release Strategy

```text
┌───────────────────────────────┬───────────────────────────────┬───────────────────────────────┐
│     Release 1: Core Ops       │   Release 2: Financial & ERP  │  Release 3: Business Auto     │
│       (12 Weeks / 6 Sprints)  │      (6 Weeks / 3 Sprints)    │      (6 Weeks / 3 Sprints)    │
├───────────────────────────────┼───────────────────────────────┼───────────────────────────────┤
│ • Customer App (Catalog/Book) │ • Payment Gateway (Razorpay/Stripe)│ • AMC Contract & Auto Cron   │
│ • Technician App (Room Cache) │ • Automated PDF Invoicing     │ • Intelligent AI Dispatching  │
│ • Admin Booking & Tech Manager│ • Chemical Batch & Trunk Stock│ • Agency Multi-Branch Portal  │
│ • Manual Dispatch Board       │ • Branch Expense & P&L Module │ • Customer WhatsApp Bot       │
│ • Spring Security & FCM Push  │ • Digital Signatures & Photos │ • Advanced Inventory Barcodes │
└───────────────────────────────┴───────────────────────────────┴───────────────────────────────┘
```

---

## 💰 Investment Summary

| Item | Details | Estimate |
| :--- | :--- | :--- |
| **Full Product Development** | 3 Releases (Core Ops, Financials, Automation) across 24 Weeks | **$38,000 – $48,000 USD**<br>*(₹31.5L – ₹40.0L INR)* |
| **Cloud Hosting & Database Run-Rate**| Spring Boot VPS, Managed PostgreSQL, Redis, RabbitMQ, SMS/OTP | **$85 – $220 / month** |
| **Warranty & Post-Launch Support** | Critical bug fixes and deployment monitoring | **30 Days Included** |
| **Annual Maintenance (Optional)** | SLA-backed support, security updates, and performance tuning | **15% of build cost / year** |

---

## 📊 Implementation Status

> **Current Phase: Architecture & Documentation Baseline**

| Component | Status |
|:---|:---|
| Architecture Documentation | ✅ Complete |
| Domain Model & SRS | ✅ Complete |
| API Specification | ✅ Complete |
| Database Design | ✅ Complete |
| Agent Skills System | ✅ Complete |
| Spring Boot Backend | 🔲 Not Yet Implemented |
| PostgreSQL Schema / Flyway | 🔲 Not Yet Implemented |
| Customer Android App | 🔲 Not Yet Implemented |
| Technician Android App | 🔲 Not Yet Implemented |
| Admin React Web App | 🔲 Not Yet Implemented |

---

*Prepared for Enterprise Management Review.*
