# ADR-001: Backend Architecture

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner
**Supersedes:** None
**Superseded by:** None
**Related:** ADR-002, ADR-004, docs/ARCHITECTURE.md, docs/MODULE_CATALOG.md
**Affected Artifacts:** docs/ARCHITECTURE.md, docs/MODULE_CATALOG.md, backend/

## Context
System needs a reliable, testable, maintainable backend for a complex ERP.

## Problem
What backend technology stack and architecture should be used for the Pest Control ERP?

## Decision
Java 21 + Spring Boot 3.x Modular Monolith via Maven.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Firebase Cloud Functions (Node.js) | stateless triggers ill-suited for complex ACID transactions, JVM ecosystem better for ERP |
| Microservices | premature complexity, distributed transaction overhead |
| PHP/Laravel | weaker JVM ecosystem for enterprise patterns |

## Consequences
### Positive
- strong typing, excellent Spring ecosystem, testable with JUnit/Testcontainers, standard deployment.

### Negative / Trade-offs
- JVM startup time (mitigated by Spring Boot 3 native/virtual threads), more initial structure.

## Status History
- September 2026: Accepted
