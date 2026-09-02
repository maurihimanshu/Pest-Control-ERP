---
name: messaging-rabbitmq-consumer
description: Skill for RabbitMQ consumer.
category: messaging
triggers:
  - consume events
inputs:
  - queues
outputs:
  - "@RabbitListener"
dependencies:
  - messaging-rabbitmq-publisher
related_skills:
  - messaging-dead-letter-queues
---

# messaging-rabbitmq-consumer

## Purpose
Skill for RabbitMQ consumer (@RabbitListener). Cover: idempotent consumer implementation, DLQ binding, retry configuration, manual ack, failed message handling, logging.

## When to Use
Processing async events from RabbitMQ.

## When NOT to Use
For synchronous processing.

## Required Context
- Queues and bindings

## Inputs
- Domain events

## Expected Outputs
- Consumer service

## Rules & Constraints
1. Consumers MUST be idempotent.
2. Must use DLQs for unprocessable messages.
3. Use manual acks if strict reliability is needed.

## Step-by-Step Workflow
1. Configure queue and DLQ bindings.
2. Implement `@RabbitListener`.
3. Check idempotency key before processing.
4. Process event and update database.
5. Ack or Nack message.

## Validation Checklist
- [ ] Idempotency is verified.
- [ ] Exceptions correctly route to DLQ.

## Common Mistakes
- Processing same message twice and creating duplicate records.

## Example Usage
```java
@RabbitListener(queues = "myQueue")
public void consume(MyEvent event) {}
```

## Related Skills
- messaging-dead-letter-queues

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
