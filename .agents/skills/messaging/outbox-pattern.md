---
name: messaging-outbox-pattern
description: Skill for Outbox Pattern.
category: messaging
triggers:
  - implement outbox
inputs:
  - database schemas
outputs:
  - outbox table
  - polling service
dependencies: []
related_skills:
  - messaging-rabbitmq-publisher
---

# messaging-outbox-pattern

## Purpose
Skill for Outbox Pattern. Cover: outbox table schema (id, aggregate_type, aggregate_id, event_type, payload, status, created_at), explicit transactional outbox writes, dedicated outbox publisher polling job.

## When to Use
Publishing events atomically with business data changes.

## When NOT to Use
For log shipping or metrics.

## Required Context
- JPA and RabbitMQ

## Inputs
- Events

## Expected Outputs
- Reliable event publishing

## Rules & Constraints
1. The command service MUST persist the business-entity change and its `outbox_events` row through the same PostgreSQL transaction and commit. If either write fails, the entire transaction MUST roll back.
2. Do NOT rely on a default `@TransactionalEventListener` to create the outbox row: its default `AFTER_COMMIT` phase runs after the business transaction and cannot provide atomic persistence. If an application event is used, its listener must participate before commit and the resulting outbox write must be verified to use the same transaction; an explicit outbox repository write in the command service is preferred.
3. A separate publisher process/thread polls committed pending rows and publishes them. It must not publish from the business transaction.

## Step-by-Step Workflow
1. Create the `outbox_events` table schema.
2. In the transactional command service, persist the domain change and the corresponding pending outbox row before commit.
3. Create a Scheduled job to claim committed pending events safely (for example, with `FOR UPDATE SKIP LOCKED`).
4. Publish to RabbitMQ. Mark the row as `PROCESSED` only after broker acknowledgement; retain or retry failures without losing the event.

## Validation Checklist
- [ ] No phantom events (published but DB rolled back).
- [ ] No dropped events (DB committed but publish failed).
- [ ] Outbox row and business mutation commit or roll back together.
- [ ] A crash after publish and before marking `PROCESSED` is safe because consumers are idempotent.

## Common Mistakes
- Publishing to RabbitMQ directly inside a `@Transactional` method.

## Example Usage
```java
// Outbox entity
```

## Related Skills
- messaging-rabbitmq-publisher

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
