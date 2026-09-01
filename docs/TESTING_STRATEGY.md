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

*Governed by enterprise software quality and automated continuous integration standards.*
