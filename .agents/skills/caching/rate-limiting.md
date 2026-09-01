---
name: caching-rate-limiting
description: Skill for Redis-based rate limiting.
category: caching
triggers:
  - implement rate limits
inputs:
  - endpoints
outputs:
  - rate limit filters
dependencies: []
related_skills:
  - api-security
---

# caching-rate-limiting

## Purpose
Skill for Redis-based rate limiting. Cover: sliding window counter, key (user_id:endpoint:minute), Spring filter or interceptor, 429 response format.

## When to Use
Protecting public APIs from abuse or brute force.

## When NOT to Use
Internal service-to-service communication.

## Required Context
- Redis

## Inputs
- Thresholds

## Expected Outputs
- 429 Too Many Requests responses

## Rules & Constraints
1. Use Redis for distributed state.
2. Return standard 429 HTTP status.

## Step-by-Step Workflow
1. Implement Interceptor or Filter.
2. Generate key `rate_limit:{ip_or_user}:{endpoint}`.
3. Increment Redis counter with TTL.
4. Block if over threshold.

## Validation Checklist
- [ ] Returns 429 on limit breach.
- [ ] Limits are per-user or per-IP.

## Common Mistakes
- Doing rate limiting in-memory on a multi-instance deployment.

## Example Usage
```java
// Rate limit logic
```

## Related Skills
- api-security

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
