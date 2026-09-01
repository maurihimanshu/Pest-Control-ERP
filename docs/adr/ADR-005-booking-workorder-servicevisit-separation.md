# ADR-005: Booking, Work Order, and Service Visit Separation

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner

## Context
Pest control involves complex job lifecycles — initial treatment, failed visit, warranty re-visit, AMC recurring visit. Collapsing these into a single entity leads to corrupt state.

## Problem
How should pest control jobs and visits be modeled to support complex lifecycles?

## Decision
Strict 3-tier domain separation: Booking (commercial) → Work Order (operational dispatch) → Service Visit (field execution). One Work Order may have MULTIPLE Service Visits (1:N).

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Single booking entity for everything | cannot model warranty/AMC/failed visits cleanly |
| Booking+Visit only | loses operational dispatch state |

## Consequences
### Positive
- clearer domain model
- supports complex job lifecycles
- better data integrity

### Negative / Trade-offs
- more tables and complexity in querying full job state.

## Status History
- September 2026: Accepted
