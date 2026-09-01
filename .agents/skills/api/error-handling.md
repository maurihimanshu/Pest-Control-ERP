---
name: api-error-handling
description: Skill for API error handling.
category: api
triggers:
  - handle errors
inputs:
  - exceptions
outputs:
  - GlobalRestControllerAdvice
dependencies: []
related_skills:
  - api-request-response-contracts
---

# api-error-handling

## Purpose
Skill for API error handling. Cover: error code conventions (DOMAIN_ENTITY_REASON format e.g. BOOKING_SLOT_UNAVAILABLE), HTTP status mapping, validation error details, global @RestControllerAdvice.

## When to Use
Standardizing how exceptions are converted to JSON.

## When NOT to Use
Swallowing exceptions silently.

## Required Context
- Spring web

## Inputs
- Exception types

## Expected Outputs
- Exception handler methods

## Rules & Constraints
1. Must use standard error codes.
2. Map to appropriate HTTP codes (400, 404, 409).
3. Do not leak stack traces to the client.

## Step-by-Step Workflow
1. Create custom business exceptions.
2. Create `@RestControllerAdvice`.
3. Add `@ExceptionHandler` for various types.
4. Format output using `ApiErrorResponse`.

## Validation Checklist
- [ ] 404 for not found.
- [ ] 400 for validation.
- [ ] No stack traces.

## Common Mistakes
- Returning 200 OK with an error payload.

## Example Usage
```java
@ExceptionHandler(ResourceNotFoundException.class)
// handler
```

## Related Skills
- api-request-response-contracts

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
