---
name: legacy-architecture-audit
description: Detects obsolete Firebase, Firestore, or Cloud Functions references in the codebase and documentation.
category: architecture
triggers:
  - audit legacy
  - find obsolete code
  - firebase audit
inputs:
  - target directory
outputs:
  - audit report with classifications
dependencies:
  - architecture-rules
related_skills:
  - architecture-discovery
---

# Skill: Legacy Architecture Audit

## Purpose
To actively root out old, forbidden architectures (Firestore for ERP data, Cloud Functions) and classify findings.

## When to Use
- During migration from legacy codebase to the canonical Spring Boot architecture.
- Periodically to ensure no regressions.

## Rules & Constraints
Classify each finding as one of:
1. `VALID_FIREBASE_SUPPORTING_USE`: Used for Auth or FCM.
2. `DOCUMENTATION_NEEDS_UPDATE`: Old markdown referencing Firestore/Functions.
3. `CODE_MUST_MIGRATE`: Existing codebase logic using Firestore/Functions.
4. `ARCHITECTURAL_VIOLATION`: New code violating the canonical architecture.

## Step-by-Step Workflow
1. Grep the repository for `firestore`, `cloud-functions`, `FirebaseDatabase`, `functions.https`.
2. Analyze the context of each match.
3. If it's a push notification or token validation, mark `VALID_FIREBASE_SUPPORTING_USE`.
4. If it's in a `.md` file, mark `DOCUMENTATION_NEEDS_UPDATE`.
5. If it's in `.java` or `.ts` performing domain logic, mark `CODE_MUST_MIGRATE` or `ARCHITECTURAL_VIOLATION`.

## Validation Checklist
- [ ] All matches classified.
- [ ] Report generated with clear file paths and line numbers.

## Common Mistakes
- Flagging FCM push notification logic as a violation.
- Flagging Firebase Auth token verification as a violation.
