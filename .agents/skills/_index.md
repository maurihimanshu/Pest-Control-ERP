---
name: master-skill-index
description: Master index of all 96 agent skills for the Pest Control ERP project — organized by category with file paths and descriptions.
category: architecture
triggers:
  - find skills
  - list skills
  - what skills are available
  - which skill should I use
  - skill index
inputs: []
outputs:
  - complete skill directory
dependencies: []
related_skills:
  - _architecture_rules
---

# 📚 Master Skill Index — Pest Control ERP Agent Skills

> **Start here.** Before using any skill, read [`_architecture_rules.md`](./_architecture_rules.md).
> Total skills: **96** across **16 categories**.

---

## 🏗️ Architecture (6 skills)

| Skill File | Description |
|:---|:---|
| [`architecture/repository-exploration.md`](./architecture/repository-exploration.md) | Systematically explore the repo structure before any task |
| [`architecture/architecture-discovery.md`](./architecture/architecture-discovery.md) | Discover and validate the current architecture from actual code |
| [`architecture/legacy-architecture-audit.md`](./architecture/legacy-architecture-audit.md) | Detect and classify obsolete Firebase/Firestore/Cloud Functions references |
| [`architecture/impact-analysis.md`](./architecture/impact-analysis.md) | Assess the cross-layer impact of a proposed change |
| [`architecture/module-boundary-validation.md`](./architecture/module-boundary-validation.md) | Validate that Spring Boot module isolation is not violated |
| [`architecture/documentation-consistency.md`](./architecture/documentation-consistency.md) | Audit all docs for consistency with the approved architecture |

---

## ⚙️ Backend — Spring Boot (12 skills)

| Skill File | Description |
|:---|:---|
| [`backend/spring-boot-module.md`](./backend/spring-boot-module.md) | Create a new Spring Boot domain module under `com.pestcontrol.modules.{domain}/` |
| [`backend/rest-controller.md`](./backend/rest-controller.md) | Design `@RestController` with DTOs, validation, auth annotations, and error mapping |
| [`backend/service-layer.md`](./backend/service-layer.md) | Design `@Service` with `@Transactional`, domain logic, and event publishing |
| [`backend/repository-layer.md`](./backend/repository-layer.md) | Design Spring Data JPA repositories with JPQL, Specifications, and projections |
| [`backend/entity-design.md`](./backend/entity-design.md) | Design `@Entity` classes with relationships, cascade, fetch strategy, optimistic locking |
| [`backend/dto-design.md`](./backend/dto-design.md) | Design request/response DTOs using Java Records and Bean Validation |
| [`backend/exception-handling.md`](./backend/exception-handling.md) | Implement `@RestControllerAdvice` with standard error envelopes |
| [`backend/transaction-management.md`](./backend/transaction-management.md) | Manage `@Transactional` propagation, isolation, and rollback rules |
| [`backend/idempotency.md`](./backend/idempotency.md) | Implement `Idempotency-Key` header and PostgreSQL deduplication table |
| [`backend/firebase-token-validation.md`](./backend/firebase-token-validation.md) | Implement `FirebaseAuthenticationFilter` in the Spring Security filter chain |
| [`backend/scheduled-jobs.md`](./backend/scheduled-jobs.md) | Implement `@Scheduled` cron jobs with idempotency and observability |
| [`backend/fcm-integration.md`](./backend/fcm-integration.md) | Send FCM HTTP v1 push notifications with error handling and DLQ fallback |

---

## 🗄️ Database — PostgreSQL & Flyway (6 skills)

| Skill File | Description |
|:---|:---|
| [`database/postgresql-schema.md`](./database/postgresql-schema.md) | Design PostgreSQL table schemas: naming, PKs, timestamps, constraints |
| [`database/flyway-migration.md`](./database/flyway-migration.md) | Create safe `V{n}__{description}.sql` Flyway migration scripts |
| [`database/relational-modeling.md`](./database/relational-modeling.md) | Model ERP entities relationally; enforce Booking→Work Order→Visit separation |
| [`database/query-optimization.md`](./database/query-optimization.md) | Optimize queries: indexes, EXPLAIN ANALYZE, pagination, N+1 prevention |
| [`database/audit-tables.md`](./database/audit-tables.md) | Design append-only `audit_logs` table — never update or delete rows |
| [`database/inventory-transactions.md`](./database/inventory-transactions.md) | Design FIFO inventory ledger with transactional deductions tied to service visits |

---

## 🏢 Domain — Business Logic (12 skills)

| Skill File | Description |
|:---|:---|
| [`domain/booking.md`](./domain/booking.md) | Booking entity, state machine (PENDING→CLOSED), business rules, APIs |
| [`domain/work-order.md`](./domain/work-order.md) | Work Order entity, dispatch state machine (ASSIGNED→COMPLETED), APIs |
| [`domain/service-visit.md`](./domain/service-visit.md) | Field execution: checklists, chemicals, photos, GPS, signature, offline sync |
| [`domain/payment.md`](./domain/payment.md) | Payment state machine, webhook HMAC, idempotent processing, COD |
| [`domain/invoice.md`](./domain/invoice.md) | PostgreSQL SEQUENCE numbering, OpenPDF, Object Storage, RabbitMQ trigger |
| [`domain/inventory.md`](./domain/inventory.md) | Batch FIFO expiry, trunk stock, warehouse hierarchy, COGS per visit |
| [`domain/amc.md`](./domain/amc.md) | Annual Maintenance Contracts, Spring `@Scheduled` cron visit generator |
| [`domain/customer.md`](./domain/customer.md) | Customer profile, address management, service history, APIs |
| [`domain/employee.md`](./domain/employee.md) | Technician profiles, skills matrix, certifications, shift management |
| [`domain/pricing.md`](./domain/pricing.md) | Server-side pricing engine: area/BHK rules, coupon validation, tax calculation |
| [`domain/dispatch.md`](./domain/dispatch.md) | Technician assignment, skill matching, Redlock slot reservation |
| [`domain/notifications.md`](./domain/notifications.md) | Multi-channel dispatch: FCM, SMS, Thymeleaf email, WhatsApp via RabbitMQ |

---

## 🔐 Security (4 skills)

| Skill File | Description |
|:---|:---|
| [`security/spring-security-config.md`](./security/spring-security-config.md) | Configure `SecurityFilterChain`, filter order, stateless sessions, permit paths |
| [`security/rbac.md`](./security/rbac.md) | 7-role RBAC with `@PreAuthorize` SpEL, method-level and resource-level checks |
| [`security/api-security.md`](./security/api-security.md) | Input validation, Redis rate limiting, HMAC webhook verification, file upload |
| [`security/security-review.md`](./security/security-review.md) | Security audit checklist: auth gaps, IDOR, injection, sensitive data exposure |

---

## 📱 Android — Customer App (4 skills)

| Skill File | Description |
|:---|:---|
| [`android/customer/auth-flow.md`](./android/customer/auth-flow.md) | Firebase phone OTP, Google Sign-In, ID token retrieval, Retrofit header |
| [`android/customer/service-catalog.md`](./android/customer/service-catalog.md) | Catalog fetch from API, local caching, search, filter, detail screen |
| [`android/customer/booking-flow.md`](./android/customer/booking-flow.md) | Service selection, address, slot picker, server-calculated price, confirmation |
| [`android/customer/payment-flow.md`](./android/customer/payment-flow.md) | Gateway SDK launch, poll server `/payments/{id}` for confirmed status |

---

## 📱 Android — Technician App (6 skills)

| Skill File | Description |
|:---|:---|
| [`android/technician/offline-first.md`](./android/technician/offline-first.md) | Room as local truth, WorkManager sync, what works offline vs online-only |
| [`android/technician/room-database.md`](./android/technician/room-database.md) | SQLCipher, entities, DAOs, offline operation queue schema |
| [`android/technician/workmanager-sync.md`](./android/technician/workmanager-sync.md) | `SyncWorker`, exponential backoff, POST `/visits/sync`, partial sync |
| [`android/technician/service-execution.md`](./android/technician/service-execution.md) | Full field flow: accept → ON_THE_WAY → ARRIVED → checklist → COMPLETED |
| [`android/technician/conflict-resolution.md`](./android/technician/conflict-resolution.md) | `operation_id`, `idempotency_key`, conflict rules, cancellation-preserving resolution |
| [`android/technician/attachment-upload.md`](./android/technician/attachment-upload.md) | Pre-signed URL pattern, WebP compression < 500 KB, retry queue |

---

## 🖥️ Admin Web — React (4 skills)

| Skill File | Description |
|:---|:---|
| [`admin/dashboard.md`](./admin/dashboard.md) | KPI cards, Recharts, loading/error states, API polling strategy |
| [`admin/dispatch-board.md`](./admin/dispatch-board.md) | Work order list, technician calendar, drag-drop assignment |
| [`admin/booking-management.md`](./admin/booking-management.md) | Booking list, filters, pagination, cancel/reschedule/assign actions |
| [`admin/reporting.md`](./admin/reporting.md) | Paginated report tables, async CSV/Excel export, date/branch filters |

---

## 🌐 API Design (5 skills)

| Skill File | Description |
|:---|:---|
| [`api/rest-design.md`](./api/rest-design.md) | `/api/v1/*` conventions, resource naming, HTTP methods, backward compat |
| [`api/request-response-contracts.md`](./api/request-response-contracts.md) | `ApiResponse<T>` wrapper, `ApiErrorResponse`, pagination envelope |
| [`api/pagination.md`](./api/pagination.md) | `page/size/sortBy/sortDir` params, keyset pagination for large datasets |
| [`api/error-handling.md`](./api/error-handling.md) | `DOMAIN_ENTITY_REASON` error codes, HTTP status mapping, validation details |
| [`api/openapi-documentation.md`](./api/openapi-documentation.md) | Springdoc `@Operation`, `@ApiResponse`, `@Schema`, module grouping |

---

## 📨 Messaging — RabbitMQ (5 skills)

| Skill File | Description |
|:---|:---|
| [`messaging/rabbitmq-publisher.md`](./messaging/rabbitmq-publisher.md) | `RabbitTemplate`, exchange/routing-key conventions, event POJO serialization |
| [`messaging/rabbitmq-consumer.md`](./messaging/rabbitmq-consumer.md) | `@RabbitListener`, idempotent consumer, DLQ binding, manual ack |
| [`messaging/event-naming.md`](./messaging/event-naming.md) | PascalCase event names, payload structure, full domain event catalog |
| [`messaging/dead-letter-queues.md`](./messaging/dead-letter-queues.md) | DLX exchange, TTL binding, DLQ depth monitoring, reprocessing strategy |
| [`messaging/outbox-pattern.md`](./messaging/outbox-pattern.md) | Atomic business and outbox writes, background publisher polling |

---

## ⚡ Caching — Redis (4 skills)

| Skill File | Description |
|:---|:---|
| [`caching/redis-caching.md`](./caching/redis-caching.md) | `@Cacheable/@CacheEvict`, key naming, TTL strategy, what to cache vs not |
| [`caching/cache-invalidation.md`](./caching/cache-invalidation.md) | Event-driven invalidation, `@CacheEvict` on writes, stampede prevention |
| [`caching/distributed-locks.md`](./caching/distributed-locks.md) | Redlock for slot reservation, lock TTL, release on exception |
| [`caching/rate-limiting.md`](./caching/rate-limiting.md) | Sliding window counter, key conventions, 429 response format |

---

## 🧪 Testing (6 skills)

| Skill File | Description |
|:---|:---|
| [`testing/unit-testing.md`](./testing/unit-testing.md) | JUnit 5 + Mockito, `givenX_whenY_thenZ` naming, state machine tests |
| [`testing/integration-testing.md`](./testing/integration-testing.md) | `@SpringBootTest`, `@Transactional` rollback, test data factories |
| [`testing/testcontainers.md`](./testing/testcontainers.md) | PostgreSQL/Redis/RabbitMQ containers, `@DynamicPropertySource`, shared instances |
| [`testing/api-contract-testing.md`](./testing/api-contract-testing.md) | MockMvc, response contract validation, auth mocking, pagination tests |
| [`testing/security-testing.md`](./testing/security-testing.md) | 401/403 enforcement, ownership checks, HMAC webhook validation tests |
| [`testing/offline-sync-testing.md`](./testing/offline-sync-testing.md) | Room migration tests, WorkManager `TestDriver`, conflict scenario tests |

---

## 🚀 DevOps (5 skills)

| Skill File | Description |
|:---|:---|
| [`devops/docker-compose-local.md`](./devops/docker-compose-local.md) | Local `docker-compose.yml` for PostgreSQL, Redis, RabbitMQ with health checks |
| [`devops/ci-cd-pipeline.md`](./devops/ci-cd-pipeline.md) | GitHub Actions: build, test (Testcontainers), Docker push, staged deploy |
| [`devops/health-checks.md`](./devops/health-checks.md) | Spring Actuator `/health`, readiness/liveness probes, custom indicators |
| [`devops/secrets-management.md`](./devops/secrets-management.md) | Env vars, GitHub secrets, no committed secrets, Firebase service account |
| [`devops/database-migration-deployment.md`](./devops/database-migration-deployment.md) | Flyway validate → migrate before Spring Boot starts, rollback strategy |

---

## 📊 Observability (4 skills)

| Skill File | Description |
|:---|:---|
| [`observability/structured-logging.md`](./observability/structured-logging.md) | SLF4J + Logback JSON, MDC correlation ID, no PII in logs |
| [`observability/metrics.md`](./observability/metrics.md) | Micrometer counters/timers/gauges, business metrics, Prometheus endpoint |
| [`observability/correlation-ids.md`](./observability/correlation-ids.md) | `X-Correlation-ID` propagation through MDC, logs, error responses, events |
| [`observability/alerting.md`](./observability/alerting.md) | Alert thresholds: DLQ depth, error rate, payment failures, sync failures |

---

## 📝 Documentation (3 skills)

| Skill File | Description |
|:---|:---|
| [`documentation/readme-update.md`](./documentation/readme-update.md) | When and what to update in README — preserve architecture diagram accuracy |
| [`documentation/adr.md`](./documentation/adr.md) | ADR format, storage at `docs/adr/`, when to create one |
| [`documentation/documentation-sync.md`](./documentation/documentation-sync.md) | Audit checklist: does README/SRS/API spec match current implementation? |

---

## 🌿 Git (3 skills)

| Skill File | Description |
|:---|:---|
| [`git/branch-strategy.md`](./git/branch-strategy.md) | `main/develop/feature/bugfix/release/hotfix` branching model |
| [`git/commit-standards.md`](./git/commit-standards.md) | Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, scope = module name |
| [`git/pull-request.md`](./git/pull-request.md) | PR description template, checklist, reviewers, link to ticket |

---

## 🔄 Workflow Orchestration (5 skills)

| Skill File | Description |
|:---|:---|
| [`workflows/feature-development.md`](./workflows/feature-development.md) | End-to-end: explore → domain model → DB → backend → API → test → doc |
| [`workflows/bug-fix.md`](./workflows/bug-fix.md) | Reproduce → root cause → minimal fix → regression test → commit |
| [`workflows/code-review.md`](./workflows/code-review.md) | Review flow: arch → security → business rules → DB → tests → docs; BLOCKER/MAJOR/MINOR |
| [`workflows/definition-of-done.md`](./workflows/definition-of-done.md) | Complete DoD checklist — a feature is NOT done until all items pass |
| [`workflows/architecture-change.md`](./workflows/architecture-change.md) | Legacy audit → ADR → incremental implementation → full re-audit |

---

## 🗺️ Skill Dependency Graph

```
_architecture_rules (MANDATORY — read first)
         │
         ▼
architecture/repository-exploration
         │
         ▼
architecture/architecture-discovery ──► architecture/legacy-architecture-audit
         │
         ▼
architecture/impact-analysis
         │
         ▼
database/relational-modeling ──► database/postgresql-schema ──► database/flyway-migration
         │
         ▼
backend/entity-design ──► backend/repository-layer ──► backend/service-layer
                                                              │
                              ┌───────────────────────────────┤
                              ▼                               ▼
                   messaging/outbox-pattern          caching/redis-caching
                              │
                              ▼
                   messaging/rabbitmq-publisher
                              │
                              ▼
                   messaging/rabbitmq-consumer ──► messaging/dead-letter-queues

backend/service-layer
         │
         ▼
backend/rest-controller ──► backend/dto-design
         │                         │
         ▼                         ▼
api/rest-design            api/request-response-contracts
         │                         │
         ▼                         ▼
api/pagination             api/error-handling
         │
         ▼
api/openapi-documentation

Cross-cutting (applied in every skill):
  security/rbac ──────────────────────► all controllers & services
  backend/idempotency ────────────────► payment, booking, sync, invoices
  backend/exception-handling ─────────► all controllers
  observability/correlation-ids ──────► all layers
  observability/structured-logging ───► all layers
  testing/* ──────────────────────────► every implementation skill
  workflows/definition-of-done ───────► every completed feature

Domain chain (never collapse):
  domain/booking ──► domain/work-order ──► domain/service-visit
       │                   │                       │
       ▼                   ▼                       ▼
  domain/payment      domain/dispatch         domain/inventory
       │                                           │
       ▼                                           ▼
  domain/invoice                         database/inventory-transactions
```

---

## ✅ Architecture Compliance Summary

| Concern | Skill(s) That Enforce It |
|:---|:---|
| PostgreSQL = System-of-Record | `_architecture_rules`, `database/*`, `domain/*` |
| Spring Boot = Core Backend | `_architecture_rules`, `backend/*`, `workflows/*` |
| Firebase Auth = IdP only | `backend/firebase-token-validation`, `security/spring-security-config` |
| FCM = Push only | `backend/fcm-integration`, `domain/notifications` |
| No Firestore as ERP DB | `_architecture_rules`, `architecture/legacy-architecture-audit` |
| No Cloud Functions | `_architecture_rules`, `architecture/legacy-architecture-audit` |
| No microservices in V1 | `_architecture_rules`, `workflows/architecture-change` |
| 3-tier domain separation | `domain/booking`, `domain/work-order`, `domain/service-visit` |
| Redis = cache/locks only | `_architecture_rules`, `caching/*` |
| RabbitMQ = async events only | `_architecture_rules`, `messaging/*` |
| Backend authority for pricing/payment | `domain/pricing`, `domain/payment`, `security/rbac` |
| Offline technician = Room + WorkManager | `android/technician/offline-first`, `android/technician/workmanager-sync` |
| Invoice = PostgreSQL SEQUENCE | `domain/invoice` |
| AMC = Spring @Scheduled | `domain/amc`, `backend/scheduled-jobs` |
| Idempotency required | `backend/idempotency`, `domain/payment`, `android/technician/conflict-resolution` |
