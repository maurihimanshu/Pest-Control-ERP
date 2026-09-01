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
Skill for Outbox Pattern. Cover: outbox table schema (id, aggregate_type, aggregate_id, event_type, payload, status, created_at), Spring @TransactionalEventListener, dedicated outbox publisher polling job.

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
1. Events MUST be saved to the `outbox` table in the same transaction as the entity.
2. A separate process/thread polls and publishes.

## Step-by-Step Workflow
1. Create `outbox` table schema.
2. Add `@TransactionalEventListener` to save event to outbox.
3. Create a Scheduled job to poll `UNPROCESSED` events.
4. Publish to RabbitMQ and mark as `PROCESSED`.

## Validation Checklist
- [ ] No phantom events (published but DB rolled back).
- [ ] No dropped events (DB committed but publish failed).

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
