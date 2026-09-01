# ADR-004: Modular Monolith

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner

## Context
Team size, complexity, initial scale don't justify distributed microservices. Modules: auth, users, customers, employees, agencies, services, pricing, bookings, scheduling, dispatch, payments, invoices, expenses, inventory, amc, notifications, support, reports, audit.

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
