---
name: technician-room-database
description: Skill for Room DB design in technician app.
category: android
triggers:
  - design room db
inputs:
  - offline requirements
outputs:
  - room entities
  - daos
dependencies:
  - technician-offline-first
related_skills:
  - technician-workmanager-sync
---

# technician-room-database

## Purpose
Skill for Room DB design in technician app. Cover: entities (AssignedJob, PendingOperation, UploadQueue), SQLCipher encryption, offline operation queue schema (operation_id, idempotency_key, type, payload, status, retry_count).

## When to Use
Designing local storage for the offline-first technician app.

## When NOT to Use
For simple caching in the customer app.

## Required Context
- Security rules
- Offline operation requirements

## Inputs
- Entity models

## Expected Outputs
- Encrypted Room Database

## Rules & Constraints
1. Must use SQLCipher for encryption.
2. Maintain offline operation queue.

## Step-by-Step Workflow
1. Define domain entities.
2. Define `PendingOperation` entity for offline actions.
3. Configure Room Database with SQLCipher.
4. Implement DAOs.

## Validation Checklist
- [ ] Database is encrypted.
- [ ] Offline queue schema is robust.

## Common Mistakes
- Storing unencrypted PII locally.
- Not keeping an operation queue.

## Example Usage
```java
// @Database setup
```

## Related Skills
- technician-offline-first

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
