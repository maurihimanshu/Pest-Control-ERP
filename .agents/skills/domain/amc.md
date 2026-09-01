---
name: amc
description: Handling Annual Maintenance Contracts (AMC).
category: domain
triggers:
  - Create AMC contract
  - Generate scheduled jobs
  - Process subscription billing
inputs:
  - Contract parameters
outputs:
  - AMC schedule generation
dependencies:
  - domain/booking
  - domain/work-order
related_skills:
  - backend/scheduled-jobs
---

# Skill: AMC (Annual Maintenance Contract) Domain

## Purpose
To manage long-term service agreements where customers pay upfront or periodically for a series of scheduled pest control visits over a time period (e.g., quarterly visits for a year).

## When to Use / When NOT to Use
**Use When:** Selling and managing multi-visit contracts, generating recurring work orders.
**NOT to Use:** For single, one-off service requests (use a standard Booking).

## Required Context
An AMC is technically a specialized type of `Booking` (or related closely to it) that spawns multiple `Work Orders` distributed across time, rather than a single immediate one.

## Domain Rules & Constraints
1. **Contract Lifecycle:** `ACTIVE`, `SUSPENDED`, `EXPIRED`, `CANCELLED`.
2. **Scheduling Engine:** A Spring `@Scheduled` cron job must run daily to scan for upcoming AMC schedules.
3. **Look-ahead Window:** Generate `Work Orders` 7 days in advance of the scheduled service date to allow the dispatch team to optimize routes.
4. **Idempotency:** The generation logic MUST be idempotent. If the cron job runs twice, it should not create duplicate `Work Orders` for the same scheduled instance.

## Entity Structure
*   `amc_contracts`: `id`, `customer_id`, `start_date`, `end_date`, `status`, `total_visits`, `frequency` (MONTHLY, QUARTERLY)
*   `amc_schedules`: `id`, `contract_id`, `expected_date`, `work_order_id` (nullable until generated), `status` (PENDING, GENERATED, SKIPPED)

## Spring Service Methods
*   `AmcContract createContract(CreateAmcDto dto)`
*   `@Scheduled(cron = "0 0 1 * * ?") void generateUpcomingWorkOrders()`

## API Endpoints
*   `POST /api/v1/amc/contracts`
*   `GET /api/v1/amc/contracts/{id}`
*   `GET /api/v1/customers/{id}/amc-contracts`

## Database Considerations
*   Ensure a unique constraint on `(contract_id, expected_date)` or similar in the schedules table to enforce idempotency at the database level.
*   Index `expected_date` and `status` heavily for the daily cron query.

## RabbitMQ Events
*   `AmcWorkOrderGeneratedEvent` -> Notifies dispatch team and customer.

## Validation Checklist
- [ ] Is the daily job idempotent?
- [ ] Are work orders generated with sufficient lead time?
- [ ] Does the contract status transition to EXPIRED automatically when time passes?

## Common Mistakes
*   Generating all 12 monthly work orders immediately upon contract signing, clogging the dispatch board for months out.
*   Failing to implement database-level unique constraints, leading to duplicate dispatch on cron job retries.

## Related Skills
- `domain/booking`
- `domain/work-order`
