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
Skill for technician field execution flow. Cover: Accept job, navigate ON_THE_WAY, ARRIVED, STARTED, checklist completion, chemical/material logging, CameraX WebP compression (<500KB), GPS capture, customer signature, hardware Android Keystore cryptographic signing (EC P-256 / SHA256withECDSA), and COMPLETED sync.

## When to Use
When building the execution flow for a specific field visit on the Android Technician App (Java 21).

## When NOT to Use
For admin-side operations.

## Required Context
- Android Native (Java 21)
- CameraX
- Room DAOs
- Android Keystore System (`AndroidKeyStore`)

## Inputs
- Job status changes and field evidence

## Expected Outputs
- Robust execution state machine with signed offline operation envelopes

## Rules & Constraints
1. Enforce canonical state transitions (`ASSIGNED -> ACCEPTED -> ON_THE_WAY -> ARRIVED -> STARTED -> COMPLETED`).
2. Compress all images to WebP (<500KB) locally before queuing.
3. **Mandatory Keystore Signing (P0-02):** Every high-risk field mutation (`START_VISIT`, `COMPLETE_VISIT`, `LOG_CHEMICALS`) MUST be cryptographically signed using the device's hardware-backed EC P-256 private key and transmitted with `X-Device-Signature`.

## Step-by-Step Workflow
1. Load visit details from Room DB.
2. Present valid state transition actions based on current status.
3. Capture checklist, chemicals used, arrival GPS, and photos.
4. Compress signatures and photos to WebP.
5. Serialize operation payload to normalized JSON.
6. Sign payload bytes using Android Keystore `Signature.getInstance("SHA256withECDSA")`.
7. Enqueue signed `PendingOperation` in Room DB for `WorkManager` background sync.

## Validation Checklist
- [ ] State machine enforces canonical progression.
- [ ] High-risk operations are signed with the Android Keystore private key.
- [ ] Images are compressed properly to WebP.
- [ ] Offline operation payload includes monotonic `local_sequence`.

## Common Mistakes
- Allowing unsigned completion payloads.
- Bypassing the local SQLite/Room store and attempting direct synchronous HTTP calls.


## Example Usage
```java
// Status update (Java 21)
```

## Related Skills
- technician-offline-first

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
