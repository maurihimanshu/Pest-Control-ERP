---
name: technician-workmanager-sync
description: Skill for WorkManager sync engine.
category: android
triggers:
  - implement sync
inputs:
  - room db operations
outputs:
  - sync worker
dependencies:
  - technician-room-database
related_skills:
  - technician-conflict-resolution
---

# technician-workmanager-sync

## Purpose
Skill for WorkManager sync engine. Cover: SyncWorker implementation, exponential backoff, network constraint, POST /api/v1/dispatch/visits/sync, partial sync handling, failed sync reporting.

## When to Use
When implementing the background synchronization engine for the technician app.

## When NOT to Use
For immediate user-facing network calls that don't need offline support.

## Required Context
- PendingOperation queue from Room

## Inputs
- Network APIs

## Expected Outputs
- WorkManager jobs

## Rules & Constraints
1. Must use exponential backoff.
2. Must run only when network is connected.
3. Implement partial sync for large queues.

## Step-by-Step Workflow
1. Create `SyncWorker` extending `CoroutineWorker`.
2. Fetch pending operations from Room.
3. Send to `/api/v1/dispatch/visits/sync`.
4. Update local statuses based on server response.

## Validation Checklist
- [ ] Network constraint applied.
- [ ] Backoff policy is exponential.

## Common Mistakes
- Syncing synchronously on the UI thread.
- Failing to handle partial successes.

## Example Usage
```kotlin
// SyncWorker implementation
```

## Related Skills
- technician-conflict-resolution

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
