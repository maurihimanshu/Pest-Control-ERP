# ADR-010: Payment Idempotency

**Status:** Accepted
**Date:** September 2026
**Deciders:** Principal Architect, Product Owner

## Context
Handling payments requires robust defense against duplicate processing or fraudulent client declarations.

## Problem
How should payment events be tracked to ensure idempotency and security?

## Decision
Payment webhook idempotency enforced via payment_events table with UNIQUE(provider, gateway_event_id). Single gateway_payment_id is insufficient because one payment can generate multiple events (authorized, captured, failed, refunded). Backend is the sole authority for payment state — client declarations of payment success are ignored.

## Alternatives Considered
| Alternative | Reason Rejected |
|:---|:---|
| Idempotent by gateway_payment_id only | cannot handle multiple events per payment |
| Client-declared payment success | fraud vector |
| Direct polling gateway | supplementary only, not primary flow |

## Consequences
### Positive
- Robust, secure handling of payment lifecycles.
- Safe from replay attacks.

### Negative / Trade-offs
- Requires persisting every payment gateway event.

## Status History
- September 2026: Accepted
