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
2. **Calendar Availability & Overlap Protection:** Overlapping technician appointments are mathematically forbidden at the database level by the PostgreSQL `ex_slot_employee_time_overlap` GiST exclusion constraint on `availability_slots`.
3. **Concurrency Control & Authority:** The authoritative correctness guarantee is PostgreSQL transaction-level row locking (`SELECT FOR UPDATE`) and exclusion constraints. An optional short-TTL Redis distributed lock (Redlock pattern) on `(agency_id, employee_id, date, time_slot)` may be used for UI contention reduction, but it NEVER replaces database validation.
4. **Tenant Scoping:** All dispatch queries and assignment commands must derive `agencyId` from the authenticated security context and filter explicitly via `findBy...AndAgencyId`.

## Spring Service Methods
*   `List<TimeSlot> getAvailableSlots(UUID agencyId, UUID skillId, LocalDate date, String zipCode)`
*   `void assignJob(UUID agencyId, UUID workOrderId, UUID employeeId)`
*   `DispatchBoardView getBoardView(UUID agencyId, LocalDate date)`

## API Endpoints
*   `GET /api/v1/dispatch/availability`
*   `POST /api/v1/dispatch/assign`
*   `GET /api/v1/dispatch/board`

## Database Considerations
*   The dispatch board query joins `work_orders`, `employees`, `customers` (for names), and `service_visits` (for current status).
*   Enforce `agency_id` on all joins and rely on PostgreSQL Row Level Security (RLS) for defense-in-depth.

## RabbitMQ Events
*   `TechnicianAssigned` -> Sent to Notification service to push to tech app.
*   `TechnicianUnassigned` -> Sent if schedule changes.

## Validation Checklist
- [ ] Is skill matching enforced?
- [ ] Are technician time overlaps blocked by PostgreSQL GiST exclusion constraint?
- [ ] Is tenant scope (`agencyId`) enforced in all repository queries?
- [ ] Can dispatchers override rules if necessary (with audit logging)?

## Common Mistakes
*   Assuming an acquired Redis lock guarantees booking safety without database-level transactional validation.
*   Querying work orders without `agencyId` scoping.


## Related Skills
- `domain/work-order`
- `domain/employee`
- `caching/distributed-locks`
