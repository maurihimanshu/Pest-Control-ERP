# ADR-009: Multi-Tenancy Agency Scope

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner

## Context
Pest control company has multiple city/regional branches. Not a SaaS platform serving independent companies.

## Problem
How should data be partitioned or scoped to support multiple agencies/branches?

## Decision
The system supports a single parent company with multiple agencies/branches as operational sub-tenants. Agencies are not fully isolated SaaS tenants — they share a single PostgreSQL schema with agency_id FK-based data segregation. All queries for agency-scoped entities MUST include agency_id in WHERE clause, enforced in the service layer by extracting agency_id from the authenticated user's profile.

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
