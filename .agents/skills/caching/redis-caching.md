---
name: caching-redis-caching
description: Skill for Redis caching with Spring Cache.
category: caching
triggers:
  - implement caching
inputs:
  - services
outputs:
  - @Cacheable annotations
dependencies: []
related_skills:
  - caching-cache-invalidation
---

# caching-redis-caching

## Purpose
Skill for Redis caching with Spring Cache. Cover: @Cacheable/@CacheEvict, key naming conventions (pestcontrol:module:entity:id), TTL strategy, cache-aside pattern, what to cache (service catalog, pricing rules) vs what NOT to cache (payment state, booking status).

## When to Use
Improving read performance on relatively static data.

## When NOT to Use
For highly transactional or rapidly changing data.

## Required Context
- Redis connection

## Inputs
- Service methods

## Expected Outputs
- Cached method returns

## Rules & Constraints
1. Use standard prefix: `pestcontrol:module:entity:id`.
2. Do not cache primary transactional data.
3. Apply sensible TTLs.

## Step-by-Step Workflow
1. Identify read-heavy static data.
2. Add `@Cacheable` to service method.
3. Configure cache TTL in Redis properties.
4. Ensure serializable DTOs.

## Validation Checklist
- [ ] Keys follow naming conventions.
- [ ] TTL is appropriate.
- [ ] Does not hide stale transactional data.

## Common Mistakes
- Caching booking status, leading to UI inconsistencies.

## Example Usage
```java
@Cacheable(value = "services", key = "'pestcontrol:services:catalog'")
public List<ServiceDto> getCatalog() {}
```

## Related Skills
- caching-cache-invalidation

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
