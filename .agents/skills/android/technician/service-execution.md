---
name: technician-service-execution
description: Skill for technician field execution flow.
category: android
triggers:
  - implement field execution
inputs:
  - service visit models
outputs:
  - execution screens
dependencies: []
related_skills:
  - technician-conflict-resolution
---

# technician-service-execution

## Purpose
Skill for technician field execution flow. Cover: Accept job, navigate ON_THE_WAY, ARRIVED, STARTED, checklist completion, chemical/material logging, CameraX WebP compression (<500KB), GPS capture, customer signature, COMPLETED sync.

## When to Use
When building the execution flow for a specific field visit.

## When NOT to Use
For admin-side operations.

## Required Context
- CameraX
- Room DAOs

## Inputs
- Job status changes

## Expected Outputs
- Execution state machine

## Rules & Constraints
1. Enforce state transitions (ASSIGNED -> ON_THE_WAY -> ARRIVED...).
2. Compress images before saving/uploading.

## Step-by-Step Workflow
1. Load job details from Room.
2. Present state transition buttons based on current state.
3. Capture checklist and materials upon STARTED.
4. Compress signatures and photos to WebP.
5. Save final state to Room and enqueue sync.

## Validation Checklist
- [ ] State machine is robust.
- [ ] Images are compressed properly.

## Common Mistakes
- Allowing invalid state transitions (e.g., STARTED to ON_THE_WAY).

## Example Usage
```kotlin
// Status update
```

## Related Skills
- technician-offline-first

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
