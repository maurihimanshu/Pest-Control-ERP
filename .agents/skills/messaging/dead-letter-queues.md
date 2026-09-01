---
name: messaging-dead-letter-queues
description: Skill for DLQ design.
category: messaging
triggers:
  - configure dlq
inputs:
  - queues
outputs:
  - dlq configurations
dependencies: []
related_skills:
  - messaging-rabbitmq-consumer
---

# messaging-dead-letter-queues

## Purpose
Skill for DLQ design. Cover: DLX exchange, TTL binding, monitoring DLQ depth, reprocessing strategy, alert threshold.

## When to Use
Setting up robust messaging infrastructure.

## When NOT to Use
For transient errors that should just be retried in-memory.

## Required Context
- RabbitMQ queues

## Inputs
- Consumer failures

## Expected Outputs
- DLX and DLQ setup

## Rules & Constraints
1. Every business queue MUST have a corresponding DLQ.
2. Monitor DLQ depth.

## Step-by-Step Workflow
1. Create a Dead Letter Exchange (DLX).
2. Create a DLQ bound to the DLX.
3. Configure the primary queue with `x-dead-letter-exchange`.
4. Setup alerts for DLQ depth > 0.
5. Create a strategy/tool to reprocess or inspect DLQ messages.

## Validation Checklist
- [ ] DLQ exists for all critical queues.
- [ ] Alerts are configured.

## Common Mistakes
- Discarding failed messages without inspection.

## Example Usage
```java
// DLQ binding
```

## Related Skills
- messaging-rabbitmq-consumer

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
