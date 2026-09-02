# ADR-003: Firebase Supporting Services

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner
**Supersedes:** None
**Superseded by:** None
**Related:** ADR-001, ADR-002, ADR-008, docs/AUTHENTICATION_AND_AUTHORIZATION.md
**Affected Artifacts:** docs/AUTHENTICATION_AND_AUTHORIZATION.md, docs/NOTIFICATION_ARCHITECTURE.md

## Context
Firebase Authentication provides excellent mobile auth (phone OTP, Google Sign-In). FCM provides reliable push delivery. Firestore/Cloud Functions are not suitable for ERP.

## Problem
What role should Firebase play in the ERP architecture?

## Decision
Firebase is ONLY used for Authentication (IdP) and Cloud Messaging (FCM). Firestore is NOT used as ERP database. Cloud Functions are NOT used as backend.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Auth0/Okta | additional cost, Firebase already provides mobile OTP natively |
| Custom auth | security risk, maintenance burden |

## Consequences
### Positive
- leverage robust identity and push messaging infrastructure natively.

### Negative / Trade-offs
- multiple vendors and integrations to manage.

## Status History
- September 2026: Accepted
