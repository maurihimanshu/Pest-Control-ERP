---
name: api-request-response-contracts
description: Skill for request/response contract design.
category: api
triggers:
  - design contracts
inputs:
  - DTOs
outputs:
  - generic response wrappers
dependencies: []
related_skills:
  - api-rest-design
---

# api-request-response-contracts

## Purpose
Skill for request/response contract design. Cover: standard ApiResponse<T> wrapper {data, message, timestamp, traceId}, ApiErrorResponse {code, message, timestamp, traceId, validationErrors[]}, pagination response {content, page, size, totalElements, totalPages}.

## When to Use
Standardizing API outputs across all controllers.

## When NOT to Use
For internal method signatures.

## Required Context
- Base classes

## Inputs
- Raw data payloads

## Expected Outputs
- Standardized JSON responses

## Rules & Constraints
1. Every successful response must be wrapped in `ApiResponse<T>`.
2. Every error must return `ApiErrorResponse`.
3. Include trace/correlation IDs in all responses.

## Step-by-Step Workflow
1. Create `ApiResponse` class.
2. Create `ApiErrorResponse` class.
3. Update controllers to return wrapped objects.
4. Update global exception handler.

## Validation Checklist
- [ ] Trace IDs are present.
- [ ] Validation errors are formatted clearly.

## Common Mistakes
- Returning raw lists instead of a wrapped response.

## Example Usage
```java
public record ApiResponse<T>(T data, String message, String traceId) {}
```

## Related Skills
- api-rest-design

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
