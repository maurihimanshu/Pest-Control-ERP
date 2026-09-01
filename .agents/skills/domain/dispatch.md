---
name: dispatch
description: Managing technician assignments, routing, and calendar availability.
category: domain
triggers:
  - Assign technician
  - View dispatch board
  - Check availability
inputs:
  - Work order requirements
outputs:
  - Dispatch assignment logic
dependencies:
  - domain/work-order
  - domain/employee
related_skills:
  - caching/redis-caching
---

# Skill: Dispatch Domain

## Purpose
To connect `Work Orders` to capable `Employees` (Technicians) based on skills, availability, and geographical territory.

## When to Use / When NOT to Use
**Use When:** Building the admin dispatch board, automatically assigning jobs, or verifying a technician has an open time slot.
**NOT to Use:** For the actual physical execution of the job (use Service Visit).

## Required Context
Dispatch is a complex scheduling problem. It requires querying multiple domains (Work Orders, Employees, Skills) and often requires concurrency control to prevent double-booking.

## Domain Rules & Constraints
1. **Skill Matching:** A technician cannot be assigned to a `Work Order` if they lack the required skill.
2. **Calendar Availability:** A technician cannot be assigned to two overlapping jobs unless explicitly overridden by a manager.
3. **Concurrency Control:** When automatically assigning or when multiple dispatchers are working, use a Redis distributed lock (Redlock pattern) on the `(employee_id, time_slot)` to prevent race conditions leading to double-booking.

## Spring Service Methods
*   `List<TimeSlot> getAvailableSlots(UUID skillId, LocalDate date, String zipCode)`
*   `void assignJob(UUID workOrderId, UUID employeeId)`
*   `DispatchBoardView getBoardView(LocalDate date, UUID agencyId)`

## API Endpoints
*   `GET /api/v1/dispatch/availability`
*   `POST /api/v1/dispatch/assign`
*   `GET /api/v1/dispatch/board`

## Database Considerations
*   The dispatch board query is heavy. It joins `work_orders`, `employees`, `customers` (for names), and `service_visits` (for current status).
*   Consider a read-optimized materialized view or Redis cache for the live dispatch board if performance degrades.

## RabbitMQ Events
*   `TechnicianAssignedEvent` -> Sent to Notification service to push to tech app.
*   `TechnicianUnassignedEvent` -> Sent if schedule changes.

## Validation Checklist
- [ ] Is skill matching enforced?
- [ ] Are race conditions for time slots mitigated using Redis distributed locks?
- [ ] Can dispatchers override rules if necessary (with audit logging)?

## Common Mistakes
*   Relying solely on database transactions without row locking or Redis locks, allowing two rapid requests to book the same technician at the same time.
*   Ignoring travel time between jobs in advanced implementations.

## Related Skills
- `domain/work-order`
- `domain/employee`
- `caching/distributed-locks`
