---
name: testing-unit-testing
description: Skill for unit testing with JUnit 5.
category: testing
triggers:
  - write tests
inputs:
  - classes
outputs:
  - unit tests
dependencies: []
related_skills:
  - testing-integration-testing
---

# testing-unit-testing

## Purpose
Skill for unit testing with JUnit 5 + Mockito. Cover: @ExtendWith(MockitoExtension.class), mock dependencies, test naming (givenX_whenY_thenZ), boundary conditions, state machine transition tests.

## When to Use
For testing core business logic and state machines in isolation.

## When NOT to Use
For testing database queries or API endpoints.

## Required Context
- JUnit 5, Mockito

## Inputs
- Target class

## Expected Outputs
- High coverage tests

## Rules & Constraints
1. Use Given/When/Then naming convention.
2. Mock external dependencies strictly.

## Step-by-Step Workflow
1. Create Test class.
2. Setup mocks using `@Mock` and `@InjectMocks`.
3. Write test cases for success, failure, and edge cases.
4. Verify mock interactions.

## Validation Checklist
- [ ] Naming convention followed.
- [ ] Boundary conditions tested.

## Common Mistakes
- Writing integration tests in unit test classes.

## Example Usage
```java
@Test
void givenValidBooking_whenConfirm_thenStatusUpdated() {}
```

## Related Skills
- testing-integration-testing

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
