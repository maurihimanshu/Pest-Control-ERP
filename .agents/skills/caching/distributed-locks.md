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
Skill for Redis distributed locks (Redlock). Cover: slot reservation pre-coordination (contention reduction), Redlock algorithm with Redisson, lock TTL, lock release on exception, and why PostgreSQL transactions/exclusion constraints remain the authoritative correctness mechanism.

## When to Use
Reducing database lock contention across multiple application instances during checkout spikes.

## When NOT to Use
Never use as the sole or final correctness mechanism for financial transactions, slot capacity, technician assignment, or inventory deductions. PostgreSQL transactions (`SELECT FOR UPDATE`, exclusion constraints) are mandatory.

## Required Context
- Redisson client
- PostgreSQL ACID transactions

## Inputs
- Contention-heavy endpoints

## Expected Outputs
- Safe distributed pre-locks with PostgreSQL transactional backing

## Rules & Constraints
1. **Redis is Non-Authoritative:** An acquired Redis lock is a preliminary optimization; the database transaction MUST still validate invariants and acquire row/table locks.
2. Always release locks in a `finally` block.
3. Always set a reasonable lock TTL to prevent deadlocks on crash.

## Step-by-Step Workflow
1. Inject `RedissonClient`.
2. Acquire lock with `tryLock(waitTime, leaseTime)`.
3. Open `@Transactional` boundary in PostgreSQL with `SELECT ... FOR UPDATE`.
4. Validate business invariants and execute database mutations.
5. Commit database transaction.
6. Release Redis lock in `finally` block.

## Validation Checklist
- [ ] Lock has TTL.
- [ ] Released properly on exception.
- [ ] Database transaction enforces actual capacity / exclusion constraints regardless of lock status.

## Common Mistakes
- Assuming an acquired Redis lock means the booking is guaranteed safe without database-level transactional validation.
- Missing lock TTL, causing indefinite lock if the node terminates.


## Example Usage
```java
// Redisson lock
```

## Related Skills
- caching-redis-caching

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
