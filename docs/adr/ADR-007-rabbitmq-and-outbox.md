# ADR-007: RabbitMQ and Outbox Pattern

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner
**Supersedes:** None
**Superseded by:** None
**Related:** ADR-001, ADR-002, docs/CONCURRENCY_AND_IDEMPOTENCY.md, docs/NOTIFICATION_ARCHITECTURE.md
**Affected Artifacts:** docs/CONCURRENCY_AND_IDEMPOTENCY.md, docs/DATABASE_DESIGN.md

## Context
Asynchronous domain reactions (such as push notifications, SMS/email alerts, PDF invoice generation, AMC visit scheduling, and low stock replenishment alerts) are triggered by business events (`PaymentCompleted`, `ServiceCompleted`, `BookingConfirmed`). Guaranteed delivery without distributed 2PC transactions is required. Crucially, core transactional business mutations (such as chemical batch inventory deductions during service visit completion) execute synchronously inside the PostgreSQL transaction, while downstream side-effects are decoupled via messaging.

## Problem
How to reliably publish domain events to message brokers without risking data inconsistency, phantom events, or event loss during broker downtime?

## Decision
1. **RabbitMQ** is used exclusively for asynchronous domain event delivery.
2. **Transactional Outbox Pattern** is the sole publication mechanism: the business transaction mutates domain entities and inserts a corresponding row into `outbox_events` within the SAME PostgreSQL transaction.
3. An independent background scheduler/poller claims committed pending events (`SELECT ... FOR UPDATE SKIP LOCKED`), publishes to RabbitMQ exchanges, and marks them `PUBLISHED`.
4. No business code may publish directly to RabbitMQ from within a `@Transactional` boundary.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Synchronous in-transaction publishing | RabbitMQ broker unavailability would break core business transactions. |
| Spring `@TransactionalEventListener(AFTER_COMMIT)` without outbox | Silent event loss if broker or application crashes immediately after commit. |
| Kafka | Deferred: higher operational overhead, overkill for V1 modular monolith scale. |
| Direct database polling without outbox table | Couples polling queries to domain entity schemas and misses transient state changes. |

## Consequences
### Positive
- Guaranteed at-least-once domain event delivery with zero phantom events.
- Core PostgreSQL ACID business transactions are fully isolated from message broker availability.
- Consumers remain idempotent and decoupled from domain command boundaries.

### Negative / Trade-offs
- Requires a dedicated outbox table and scheduled polling process.

## Status History
- September 2026: Accepted
