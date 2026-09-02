---
name: technician-conflict-resolution
description: Skill for offline conflict resolution.
category: android
triggers:
  - resolve conflicts
inputs:
  - sync responses
outputs:
  - conflict logic
dependencies: []
related_skills:
  - technician-workmanager-sync
---

# technician-conflict-resolution

## Purpose
Skill for offline conflict resolution. Cover: operation_id, idempotency_key, client_timestamp, server_timestamp, retry_count, sync_status fields. An offline completion must not override an online administrative cancellation; create a conflict record and require an authorized resolution with an audit log. Backend is authoritative. Never blindly overwrite server state.

## When to Use
When designing backend and frontend logic for syncing offline data.

## When NOT to Use
For real-time concurrent editing.

## Required Context
- Sync models

## Inputs
- Sync payloads

## Expected Outputs
- Safe data merging

## Rules & Constraints
1. Backend is always authoritative.
2. An administrative cancellation remains authoritative when a later offline completion is synchronized. Preserve the submitted completion evidence and create a conflict record rather than changing the cancelled state.
3. Only an authorized DISPATCHER or ADMIN may resolve the conflict, and the decision must be recorded in `audit_logs`.

## Step-by-Step Workflow
1. Receive sync payload on backend.
2. Compare timestamps and state machines.
3. If completion conflicts with cancellation, retain the server cancellation and create a conflict record for authorized resolution.
4. Return the resolved state and conflict status to the client.
5. Client updates Room DB to match server.

## Validation Checklist
- [ ] Idempotency keys prevent duplicate operations.
- [ ] Conflicts are logged.
- [ ] Offline completion never silently changes a cancelled visit to completed.

## Common Mistakes
- Client blindly forcing updates.

## Example Usage
```java
// Conflict logic
```

## Related Skills
- technician-workmanager-sync

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
