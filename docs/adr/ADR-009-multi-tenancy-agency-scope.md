# ADR-009: Multi-Tenancy Agency Scope

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner
**Supersedes:** None
**Superseded by:** ADR-015
**Related:** ADR-002, ADR-008, docs/CONCURRENCY_AND_IDEMPOTENCY.md, docs/ARCHITECTURE.md
**Affected Artifacts:** docs/CONCURRENCY_AND_IDEMPOTENCY.md, docs/DATABASE_DESIGN.md, docs/TESTING_STRATEGY.md

## Context
Pest control company has multiple city/regional branches. Not a SaaS platform serving independent companies.

## Problem
How should data be partitioned or scoped to support multiple agencies/branches?

## Decision
Superseded by ADR-015. The shared-schema, `agency_id` model remains, but it is now enforced by both application scoping and PostgreSQL Row Level Security.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Row-level security (PostgreSQL RLS) | deferred: adds complexity, harder to test, revisit if security requirement tightens |
| Separate schemas per agency | rejected: operational overhead, migration complexity |
| Full multi-tenant SaaS | not required for V1 |

## Consequences
### Positive
- Simpler database migrations and reporting.
- Easy to manage shared global data (service catalogs).

### Negative / Trade-offs
- Risk of developer error omitting agency_id from queries (requires careful service layer design).

## Status History
- September 2026: Accepted
- September 2026: Superseded by ADR-015 (RLS defense-in-depth is required in V1)
