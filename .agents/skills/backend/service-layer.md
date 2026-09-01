---
name: service-layer
description: Designs Spring service layer with transactional boundaries, domain logic, and event publishing.
category: backend
triggers:
  - create service
  - add business logic
inputs:
  - domain context
  - use cases
outputs:
  - Service interface and implementation
dependencies:
  - repository-layer
  - transaction-management
related_skills:
  - idempotency
---

# Skill: Service Layer Design

## Purpose
To encapsulate core business logic, coordinate domain models, and manage transaction boundaries in a safe, predictable way.

## Rules & Constraints
1. Always define an interface (e.g., `BookingService`) and an implementation class (e.g., `BookingServiceImpl`).
2. Annotate implementations with `@Service` and `@RequiredArgsConstructor`.
3. Use constructor injection (`final` fields) for dependencies.
4. Place `@Transactional` at the method or class level depending on read/write needs.
5. Emitting domain events (e.g., via `ApplicationEventPublisher` or RabbitMQ) must happen within or immediately after successful transactions (consider Outbox pattern).

## Step-by-Step Workflow
1. Define the Service interface in the module's `service` package.
2. Implement the interface.
3. Inject Repositories, other internal Services, or event publishers.
4. Implement business use cases, checking pre-conditions and throwing appropriate domain exceptions (e.g., `ResourceNotFoundException`, `InvalidStateException`).
5. Ensure state changes are saved via Repository calls before returning.

## Validation Checklist
- [ ] Interface and Implementation separation.
- [ ] No direct REST/HTTP dependencies (e.g., `HttpServletRequest`).
- [ ] Transactions correctly demarcated.

## Common Mistakes
- Catching exceptions silently without rolling back the transaction.
- Making external API calls or sending emails synchronously inside a `@Transactional` block (can exhaust connection pools).
