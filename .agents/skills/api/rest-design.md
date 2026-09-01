---
name: api-rest-design
description: Skill for REST API design standards.
category: api
triggers:
  - design api
  - create endpoint
inputs:
  - domain models
outputs:
  - controllers
  - specs
dependencies: []
related_skills:
  - api-request-response-contracts
---

# api-rest-design

## Purpose
Skill for REST API design standards. Cover: /api/v1/* prefix, resource naming (nouns, plural), HTTP methods, status codes, CRUD vs action endpoints (/bookings/{id}/confirm), backward compatibility rules.

## When to Use
When creating new REST endpoints in the Spring Boot backend.

## When NOT to Use
For internal messaging or cron jobs.

## Required Context
- Domain models

## Inputs
- Business requirements

## Expected Outputs
- Standardized REST controller

## Rules & Constraints
1. Use `/api/v1` prefix.
2. Plural nouns for resources.
3. Actions use sub-paths (`/cancel`).

## Step-by-Step Workflow
1. Identify resource.
2. Map standard CRUD to HTTP methods (GET, POST, PUT, DELETE).
3. Map actions to POST with action verbs.
4. Ensure appropriate status codes (200, 201, 204).

## Validation Checklist
- [ ] Conforms to REST standards.
- [ ] No verbs in base resource path.

## Common Mistakes
- `POST /createBooking` instead of `POST /bookings`.

## Example Usage
```java
@PostMapping("/{id}/confirm")
public void confirm(@PathVariable UUID id) {}
```

## Related Skills
- api-request-response-contracts

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
