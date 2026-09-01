# ADR-011: Inventory Concurrency

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner

## Context
Multiple technicians may simultaneously try to use from the same chemical batch. Must prevent negative inventory without application-level race conditions.

## Problem
How to safely handle concurrent inventory deductions?

## Decision
Inventory deductions are transactional using PostgreSQL SELECT FOR UPDATE with a CHECK CONSTRAINT (current_quantity >= 0). Deductions happen in the same transaction as service visit completion. Rollback via compensating REVERSAL transaction (not undone — creates audit trail).

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Application-level check without DB lock | TOCTOU race condition |
| Pessimistic row lock without constraint | constraint provides additional DB-level safety net |

## Consequences
### Positive
- Prevents negative inventory robustly.
- Audit trail preserved via reversal transactions.

### Negative / Trade-offs
- Row locks could cause contention if many technicians use the exact same batch concurrently.

## Status History
- September 2026: Accepted
