# ADR-004: Modular Monolith

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner
**Supersedes:** None
**Superseded by:** None
**Related:** ADR-001, docs/MODULE_CATALOG.md, docs/ARCHITECTURE.md
**Affected Artifacts:** docs/MODULE_CATALOG.md, docs/ARCHITECTURE.md, .agents/skills/_architecture_rules.md

## Context
Team size, complexity, and initial scale do not justify distributed microservices. The canonical 18 modules are defined in `docs/MODULE_CATALOG.md`: auth, users, customers, employees, agencies, catalog, bookings, dispatch, payments, inventory, expenses, amc, notifications, support, files, reporting, audit, and outbox.

## Problem
How should the backend application be structured to balance maintainability and complexity?

## Decision
V1 backend is a Modular Monolith — single deployable JAR with 18 logically isolated domain modules.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Microservices | distributed transaction overhead, operational complexity, premature optimization |
| Layered monolith (no module boundaries) | leads to big ball of mud, impossible to extract later |

## Consequences
### Positive
- simpler deployment and testing
- avoiding distributed data management
- future extraction via Strangler Fig if scale/team justifies

### Negative / Trade-offs
- requires strict discipline to prevent spaghetti dependencies between modules.

## Status History
- September 2026: Accepted
