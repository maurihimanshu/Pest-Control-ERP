# ADR-008: Authentication and Authorization

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner
**Supersedes:** None
**Superseded by:** None
**Related:** ADR-003, ADR-009, docs/AUTHENTICATION_AND_AUTHORIZATION.md, docs/RBAC_AND_PERMISSIONS.md
**Affected Artifacts:** docs/AUTHENTICATION_AND_AUTHORIZATION.md, docs/RBAC_AND_PERMISSIONS.md, SECURITY.md

## Context
Mobile apps need Firebase phone OTP and Google Sign-In. Backend needs RBAC from a relational model.

## Problem
How should authentication and authorization be implemented across mobile and backend?

## Decision
Firebase Authentication verifies identity (issues signed JWTs). Spring Security (FirebaseAuthenticationFilter) validates the JWT and loads authorization context from PostgreSQL (roles, is_active, agency_id). Authorization is 100% server-side. User deactivation (is_active=false in PostgreSQL) immediately rejects all requests regardless of Firebase token validity.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Firestore Security Rules | client-side rules are not a backend authorization boundary |
| Keycloak/Auth0 | Firebase already provides mobile auth |
| JWT-only without PostgreSQL lookup | cannot enforce is_active or RBAC changes without token re-issue |

## Consequences
### Positive
- Immediate user deactivation works robustly.
- Real-time RBAC via DB lookups.

### Negative / Trade-offs
- Database hit on authenticated requests (can be mitigated with short-lived caching).

## Status History
- September 2026: Accepted
