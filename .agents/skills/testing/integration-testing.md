---
name: testing-integration-testing
description: Skill for Spring Boot integration testing.
category: testing
triggers:
  - write integration tests
inputs:
  - controllers
  - repositories
outputs:
  - integration tests
dependencies:
  - testing-testcontainers
related_skills:
  - testing-api-contract-testing
---

# testing-integration-testing

## Purpose
Skill for Spring Boot integration testing. Cover: @SpringBootTest, @TestPropertySource, Testcontainers for PostgreSQL + Redis + RabbitMQ, @Transactional test rollback, test data factories.

## When to Use
Testing complete slices of the application (DB + Service + API).

## When NOT to Use
For exhaustive permutations of complex business logic (use unit tests).

## Required Context
- Spring Boot Test

## Inputs
- Endpoints and workflows

## Expected Outputs
- Slices tested against real DB

## Rules & Constraints
1. MUST use Testcontainers (no H2).
2. Tests should rollback transactions to stay isolated.

## Step-by-Step Workflow
1. Annotate with `@SpringBootTest`.
2. Configure Testcontainers base class.
3. Write end-to-end flows.

## Validation Checklist
- [ ] Tests run against Postgres, not H2.
- [ ] Rollback after each test.

## Common Mistakes
- Using H2 and missing Postgres-specific SQL errors.

## Example Usage
```java
@SpringBootTest
class BookingFlowIT {}
```

## Related Skills
- testing-testcontainers

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
