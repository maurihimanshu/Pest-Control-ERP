---
name: scheduled-jobs
description: Designs Spring @Scheduled jobs with idempotency and observability.
category: backend
triggers:
  - create cron job
  - schedule task
inputs:
  - job requirements
  - timing/cron
outputs:
  - Scheduled Component
dependencies:
  - service-layer
related_skills:
  - transaction-management
---

# Skill: Scheduled Jobs

## Purpose
To execute recurring background tasks (e.g., generating daily reports, syncing inventory, archiving data) directly within the monolithic backend.

## Rules & Constraints
1. Annotate a configuration class with `@EnableScheduling`.
2. Create a `@Component` and use `@Scheduled(cron = "...")`.
3. In a multi-node deployment, Spring `@Scheduled` runs on ALL nodes. **Canonical Multi-Node Pattern**:
   ```text
   Spring @Scheduled
          ↓
   PostgreSQL Transaction Advisory Lock: SELECT pg_try_advisory_xact_lock(hashtext('job_name'))
          ↓ (If acquired -> execute; If not acquired -> skip execution immediately)
   @Transactional Service Execution
          ↓
   Database-Level Uniqueness & Idempotency Invariants (e.g. UNIQUE(contract_id, visit_sequence))
   ```
4. Keep the `@Scheduled` method thin; it should acquire the advisory lock and delegate to a `@Transactional` Service method.
5. **Database Invariant Defense**: The business operation MUST maintain database uniqueness/idempotency invariants so correctness does not depend solely on scheduler locks.

## Step-by-Step Workflow
1. Create the scheduled component class.
2. Open a transaction and execute `SELECT pg_try_advisory_xact_lock(hashtext(:jobKey))`.
3. If lock is `FALSE`, log debug and return immediately.
4. If lock is `TRUE`, invoke the target `@Transactional` service.
5. Record execution in `audit_logs` and log structured metrics.
6. Commit transaction (automatically releasing the transaction-level advisory lock).

## Validation Checklist
- [ ] PostgreSQL advisory lock (`pg_try_advisory_xact_lock`) is acquired before execution.
- [ ] Database-level unique constraint prevents duplicate generation if two instances somehow race.
- [ ] Cron expression is valid.
- [ ] Exceptions are caught and logged with MDC correlation context.

## Common Mistakes
- Relying purely on application-level locks without database uniqueness constraints.
- Placing `@Transactional` on the scheduled method itself instead of delegating to a separate Spring service bean.

