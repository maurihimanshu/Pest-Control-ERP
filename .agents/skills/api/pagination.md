---
name: api-pagination
description: Skill for API pagination.
category: api
triggers:
  - implement pagination
inputs:
  - list endpoints
outputs:
  - pageable responses
dependencies: []
related_skills:
  - api-request-response-contracts
---

# api-pagination

## Purpose
Skill for API pagination. Cover: request params (page, size, sortBy, sortDir), keyset pagination for large datasets, max page size enforcement, response envelope.

## When to Use
Returning lists of data (bookings, users, services).

## When NOT to Use
For single item lookups or small fixed lists (e.g., roles).

## Required Context
- Spring Data JPA

## Inputs
- Queries

## Expected Outputs
- Paginated endpoint

## Rules & Constraints
1. Enforce max page size (e.g., 100) to prevent OOM.
2. Use Keyset pagination if table is massive.

## Step-by-Step Workflow
1. Accept `Pageable` in controller or discrete parameters.
2. Pass to Repository.
3. Map `Page<T>` to custom pagination response envelope.

## Validation Checklist
- [ ] Max size is enforced.
- [ ] Default sorting is applied.

## Common Mistakes
- Fetching all records and slicing in memory.

## Example Usage
```java
// Pageable usage
```

## Related Skills
- api-request-response-contracts

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
