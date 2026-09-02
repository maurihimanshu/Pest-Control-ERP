# ADR-012: Invoice Numbering

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner
**Supersedes:** None
**Superseded by:** None
**Related:** ADR-002, ADR-010, docs/PAYMENT_ARCHITECTURE.md, docs/DATABASE_DESIGN.md
**Affected Artifacts:** docs/PAYMENT_ARCHITECTURE.md, docs/DATABASE_DESIGN.md

## Context
Need sequential, unique, non-repeatable invoice numbers for financial/legal compliance.

## Problem
How to generate sequential invoice numbers safely under concurrency?

## Decision
Invoice numbers are generated using PostgreSQL `invoice_seq`. Format: `INV-{YYYY}-{NNNNN padded to 5 digits}`. `nextval()` is non-transactional, so values can be skipped after rollbacks or failed attempts; uniqueness and monotonic allocation are guaranteed, gaplessness is not.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Firestore atomic counters | rejected (ADR-002) |
| Application UUID | not human-readable |
| MAX()+1 approach | race condition under concurrent inserts |

## Consequences
### Positive
- Fast, concurrent-safe sequential number generation.
- Human-readable format.

### Negative / Trade-offs
- Sequences will have gaps upon transaction rollbacks.

## Status History
- September 2026: Accepted
