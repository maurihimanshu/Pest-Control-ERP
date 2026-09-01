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
3. In a multi-node deployment, Spring `@Scheduled` will run on ALL nodes. **You MUST use distributed locks** (e.g., Redis via ShedLock) to ensure only one instance executes the job.
4. Keep the `@Scheduled` method thin; it should call a `@Transactional` Service method.

## Step-by-Step Workflow
1. Add ShedLock dependency and configure it with Redis or PostgreSQL provider.
2. Create the job class.
3. Apply `@Scheduled` and `@SchedulerLock(name = "jobName", lockAtLeastFor = "...", lockAtMostFor = "...")`.
4. Delegate to the Service layer.
5. Log start, completion, and any errors with appropriate context.

## Validation Checklist
- [ ] ShedLock or similar distributed locking is applied.
- [ ] Cron expression is valid.
- [ ] Exceptions are caught and logged (uncaught exceptions in scheduled tasks do not crash the app, but they fail silently if not logged).

## Common Mistakes
- Forgetting distributed locking, causing duplicate emails or double processing in production.
- Placing `@Transactional` on the scheduled method itself instead of the inner service method, which can sometimes lead to proxy issues depending on class structure.
