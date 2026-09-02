# ADR-006: Offline Synchronization

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner
**Supersedes:** None
**Superseded by:** ADR-015
**Related:** ADR-005, docs/CONCURRENCY_AND_IDEMPOTENCY.md, docs/OFFLINE_SYNC.md
**Affected Artifacts:** docs/OFFLINE_SYNC.md, docs/CONCURRENCY_AND_IDEMPOTENCY.md, docs/DATABASE_DESIGN.md

## Context
Field technicians operate in areas with poor connectivity. Data must not be lost. Device-bound signing was later made a V1 security requirement; see ADR-015.

## Problem
How should the technician Android App handle offline scenarios and data synchronization?

## Decision
Superseded by ADR-015. Retained only as the historical V1 simplification decision.

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
- September 2026: Superseded by ADR-015 (device-bound signing is required in V1)
