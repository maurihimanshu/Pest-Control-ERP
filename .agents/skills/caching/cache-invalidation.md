---
name: caching-cache-invalidation
description: Skill for cache invalidation.
category: caching
triggers:
  - invalidate cache
inputs:
  - update methods
outputs:
  - "@CacheEvict logic"
dependencies: []
related_skills:
  - caching-redis-caching
---

# caching-cache-invalidation

## Purpose
Skill for cache invalidation. Cover: event-driven invalidation on data change, @CacheEvict on writes, TTL-based expiry, cache stampede prevention (probabilistic early expiry).

## When to Use
When updating data that is currently cached.

## When NOT to Use
If you aren't caching the data in the first place.

## Required Context
- `@Cacheable` methods

## Inputs
- Mutation logic

## Expected Outputs
- Cache eviction

## Rules & Constraints
1. Must evict on every related write/update/delete.
2. Use event-driven invalidation for distributed changes.

## Step-by-Step Workflow
1. Identify methods that modify cached data.
2. Add `@CacheEvict(value = "...", key = "...")`.
3. For complex cases, use Spring Events to trigger eviction.

## Validation Checklist
- [ ] Cache clears immediately upon write.
- [ ] No stale data served post-update.

## Common Mistakes
- Updating the DB but forgetting to clear the cache.

## Example Usage
```java
@CacheEvict(value = "services", allEntries = true)
public void updateService() {}
```

## Related Skills
- caching-redis-caching

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
