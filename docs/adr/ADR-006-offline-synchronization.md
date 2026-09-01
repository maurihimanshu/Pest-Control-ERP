# ADR-006: Offline Synchronization

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner

## Context
Field technicians operate in areas with poor connectivity. Data must not be lost. Cryptographic signing adds key management complexity not justified for V1.

## Problem
How should the technician Android App handle offline scenarios and data synchronization?

## Decision
Technician Android App is offline-first using Room SQLite + SQLCipher + WorkManager + server-side idempotency. NO cryptographic payload signing in V1 — replaced by Firebase JWT authentication + operation_id idempotency + server-side state validation + audit logging.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Online-only app | unusable in field |
| Full cryptographic signing | deferred: Android Keystore + Ed25519 + server public key registry adds significant complexity. Phase 2 option. |

## Consequences
### Positive
- technician can work offline
- operations sync reliably with idempotency
- audit trail maintained even without crypto signing

### Negative / Trade-offs
- no strict non-repudiation guarantees on offline payloads for V1.

## Status History
- September 2026: Accepted
