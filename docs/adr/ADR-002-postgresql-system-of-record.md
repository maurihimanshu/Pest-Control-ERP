# ADR-002: PostgreSQL System of Record

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner
**Supersedes:** None
**Superseded by:** None
**Related:** ADR-001, ADR-003, ADR-011, docs/DATABASE_DESIGN.md
**Affected Artifacts:** docs/DATABASE_DESIGN.md, docs/CONCURRENCY_AND_IDEMPOTENCY.md

## Context
ERP data requires ACID transactions, relational integrity, complex queries, and reliable audit trails.

## Problem
What database should serve as the authoritative system-of-record for the ERP?

## Decision
PostgreSQL 16 is the sole authoritative ERP system-of-record.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Firebase Firestore | eventual consistency, no true JOIN, transaction limits, poor ERP reporting |
| MongoDB | weaker ACID semantics, document model ill-suited for relational ERP |

## Consequences
### Positive
- all financial, operational, and customer data in one reliable store
- enables complex reporting queries
- enables proper foreign keys and constraints
- requires proper schema design and Flyway migrations

### Negative / Trade-offs
- requires proper schema design and Flyway migrations (can be seen as positive for structure, but requires effort)

## Status History
- September 2026: Accepted
