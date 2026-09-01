---
name: messaging-event-naming
description: Skill for event naming conventions.
category: messaging
triggers:
  - define events
inputs:
  - domain actions
outputs:
  - event schemas
dependencies: []
related_skills:
  - messaging-rabbitmq-publisher
---

# messaging-event-naming

## Purpose
Skill for event naming conventions. Cover: PascalCase event names (BookingCreated, PaymentCompleted, etc.), event POJO structure {eventId, occurredAt, version, payload}, list of domain events for this project.

## When to Use
Designing new events for async processes.

## When NOT to Use
For internal method names or synchronous DTOs.

## Required Context
- Event payload

## Inputs
- Business actions

## Expected Outputs
- Named event POJOs

## Rules & Constraints
1. Events MUST be named in past tense (`BookingCreated`, not `CreateBooking`).
2. Include standard metadata: `eventId`, `occurredAt`, `version`.

## Step-by-Step Workflow
1. Identify the domain state change.
2. Name the event (e.g., `ServiceVisitCompleted`).
3. Define the POJO with metadata and payload.
4. Add to event registry/documentation.

## Validation Checklist
- [ ] Name is PascalCase and past tense.
- [ ] Contains `eventId` and `occurredAt`.

## Common Mistakes
- Naming events as commands (`SendEmail`).

## Example Usage
```java
public record BookingCreated(UUID eventId, Instant occurredAt, BookingPayload payload) {}
```

## Related Skills
- messaging-rabbitmq-publisher

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
