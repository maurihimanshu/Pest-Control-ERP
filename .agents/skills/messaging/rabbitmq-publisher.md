---
name: messaging-rabbitmq-publisher
description: Skill for RabbitMQ event publishing.
category: messaging
triggers:
  - publish event
  - send message
inputs:
  - domain events
outputs:
  - publisher service
dependencies:
  - messaging-outbox-pattern
related_skills:
  - messaging-rabbitmq-consumer
---

# messaging-rabbitmq-publisher

## Purpose
Skill for RabbitMQ event publishing from Spring Boot. Cover: RabbitTemplate, exchange/routing-key naming conventions, event POJO serialization, transactional outbox pattern for reliable publication.

## When to Use
When publishing domain events to RabbitMQ.

## When NOT to Use
For direct synchronous service-to-service calls.

## Required Context
- RabbitMQ setup

## Inputs
- Event payload

## Expected Outputs
- Reliable publishing logic

## Rules & Constraints
1. MUST use Transactional Outbox pattern to prevent dual-write problems.
2. Serialize payloads to JSON.

## Step-by-Step Workflow
1. Create Event POJO.
2. Save event to outbox table in same transaction as business logic.
3. Async worker polls outbox and uses RabbitTemplate to publish.

## Validation Checklist
- [ ] Outbox pattern used.
- [ ] Correct exchange and routing keys.

## Common Mistakes
- Publishing directly in the business transaction, leading to phantom events on rollback.

## Example Usage
```java
// Outbox save
```

## Related Skills
- messaging-outbox-pattern

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
