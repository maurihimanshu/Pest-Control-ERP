---
name: testing-testcontainers
description: Skill for Testcontainers setup.
category: testing
triggers:
  - setup testcontainers
inputs:
  - application context
outputs:
  - base test classes
dependencies: []
related_skills:
  - testing-integration-testing
---

# testing-testcontainers

## Purpose
Skill for Testcontainers setup. Cover: PostgreSQLContainer, GenericContainer for Redis/RabbitMQ, @DynamicPropertySource, shared static containers, module-specific test base classes.

## When to Use
Setting up or modifying the integration testing environment.

## When NOT to Use
In production code.

## Required Context
- Docker environment

## Inputs
- Required infrastructure

## Expected Outputs
- Base IT class

## Rules & Constraints
1. Use singleton containers to speed up tests.
2. Bind properties via `@DynamicPropertySource`.

## Step-by-Step Workflow
1. Define static `PostgreSQLContainer`.
2. Define static Redis/RabbitMQ containers.
3. Start in static block.
4. Provide config variables to Spring context.

## Validation Checklist
- [ ] Containers start successfully.
- [ ] Reused across test classes.

## Common Mistakes
- Starting and stopping containers per test class (very slow).

## Example Usage
```java
// AbstractIntegrationTest
```

## Related Skills
- testing-integration-testing

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
