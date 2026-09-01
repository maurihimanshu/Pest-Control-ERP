# ADR-013: AMC Scheduling

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner

## Context
Annual Maintenance Contracts require automatic recurring visit scheduling.

## Problem
How to automatically and reliably schedule AMC recurring visits?

## Decision
AMC recurring visit generation uses Spring @Scheduled daily cron job running at 01:00 UTC. Job generates work orders for AMC schedules due within the next 7 days. Generation is idempotent (INSERT ... ON CONFLICT DO NOTHING using amc_schedule_id + scheduled_date unique constraint).

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Firebase Cloud Scheduler | rejected (ADR-003) |
| Quartz Scheduler | deferred as future option for HA/clustered scheduling if single-node Spring @Scheduled proves insufficient |

## Consequences
### Positive
- Simple to implement and maintain in V1.
- Safe from duplicate scheduling due to DB constraints.

### Negative / Trade-offs
- Single node execution required to avoid redundant processing, or DB locks if multi-node.

## Status History
- September 2026: Accepted
