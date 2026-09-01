# ADR-007: RabbitMQ and Outbox Pattern

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner

## Context
Decoupled notification, invoicing, inventory deduction triggered by domain events (PaymentCompleted, ServiceCompleted). Need guaranteed delivery without distributed 2PC.

## Problem
How to reliably publish domain events to message brokers without risking data inconsistency?

## Decision
RabbitMQ for async domain event delivery. Outbox Pattern for reliable event publication (business transaction + outbox_events row in same PostgreSQL COMMIT, then background publisher polls and publishes to RabbitMQ).

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Synchronous in-transaction publishing | RabbitMQ broker unavailability would break core transactions |
| Kafka | deferred: higher operational overhead, overkill for V1 scale |
| Database polling without outbox | misses events if publishing fails |

## Consequences
### Positive
- Guaranteed at-least-once event delivery.
- Core transactions isolated from message broker availability.

### Negative / Trade-offs
- Requires background polling component for the outbox table.

## Status History
- September 2026: Accepted
