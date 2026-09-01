---
name: caching-distributed-locks
description: Skill for Redis distributed locks.
category: caching
triggers:
  - implement locks
inputs:
  - concurrency issues
outputs:
  - Redisson lock usage
dependencies: []
related_skills:
  - caching-redis-caching
---

# caching-distributed-locks

## Purpose
Skill for Redis distributed locks (Redlock). Cover: slot reservation locking (booking slot concurrency), Redlock algorithm with Redisson, lock TTL, lock release on exception, when to use vs when PostgreSQL advisory locks are sufficient.

## When to Use
Preventing race conditions across multiple instances (e.g., slot booking).

## When NOT to Use
For single-instance locks or simple DB row updates (use DB locks).

## Required Context
- Redisson client

## Inputs
- Critical sections

## Expected Outputs
- Safe distributed locks

## Rules & Constraints
1. Always release locks in a `finally` block.
2. Always set a reasonable lock TTL to prevent deadlocks on crash.

## Step-by-Step Workflow
1. Inject RedissonClient.
2. Acquire lock with `tryLock(waitTime, leaseTime)`.
3. Execute critical section.
4. Release lock in `finally`.

## Validation Checklist
- [ ] Lock has TTL.
- [ ] Released properly on exception.
- [ ] Prevents double-booking.

## Common Mistakes
- Not setting a TTL, causing indefinite lock if the server dies.

## Example Usage
```java
// Redisson lock
```

## Related Skills
- caching-redis-caching

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
