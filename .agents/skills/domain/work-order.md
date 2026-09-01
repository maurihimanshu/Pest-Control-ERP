---
name: work-order
description: Handling the Work Order domain for operational dispatch.
category: domain
triggers:
  - Dispatch a job
  - Generate work orders
  - Manage technician assignments
inputs:
  - Booking confirmation
outputs:
  - Work order service implementation
dependencies:
  - domain/booking
related_skills:
  - domain/service-visit
  - domain/dispatch
---

# Skill: Work Order Domain

## Purpose
To manage `Work Orders`, which serve as the operational dispatch grouping for a specific occurrence of service derived from a `Booking`.

## When to Use / When NOT to Use
**Use When:** Assigning technicians to jobs, managing the daily schedule, and tracking the high-level progress of dispatch execution.
**NOT to Use:** For billing/invoicing (use Booking/Invoice) or capturing granular on-site task completion like photos (use Service Visit).

## Required Context
A `Booking` for a single service will usually spawn one `Work Order`. An AMC `Booking` for a year might spawn 4 `Work Orders` scheduled out over the year.

## Domain Rules & Constraints
1. **Assignment:** A Work Order is assigned to an `employee` (Technician) and often falls under a specific `agency_id` (Franchise/Branch).
2. **State Machine:**
   `UNASSIGNED` -> `ASSIGNED` -> `ACCEPTED` / `REJECTED` (by technician)
   If `ACCEPTED`: -> `ON_THE_WAY` -> `ARRIVED` -> `STARTED` -> `COMPLETED`
   If `REJECTED`: -> returns to `UNASSIGNED` for redispatch.
3. **Relationship:**
   * Belongs to 1 `Booking`.
   * Has 1 or more `Service Visits`. If a tech cannot finish the job and must return the next day, a second `Service Visit` is created under the same `Work Order`.

## Entity Structure
*   `id` UUID
*   `booking_id` UUID (FK)
*   `assigned_employee_id` UUID (FK, Nullable initially)
*   `agency_id` UUID (FK)
*   `scheduled_date` TIMESTAMP
*   `status` VARCHAR
*   `notes` TEXT
*   `created_at`, `updated_at`

## Spring Service Methods
*   `WorkOrder assignTechnician(UUID workOrderId, UUID employeeId)`
*   `WorkOrder updateStatus(UUID workOrderId, String newStatus)`
*   `List<WorkOrder> getDailySchedule(UUID employeeId, LocalDate date)`

## API Endpoints
*   `GET /api/v1/dispatch/work-orders` (Admin view)
*   `GET /api/v1/dispatch/technician/{empId}/schedule` (Tech view)
*   `PUT /api/v1/dispatch/work-orders/{id}/status`
*   `POST /api/v1/dispatch/work-orders/{id}/assign`

## Database Considerations
*   Heavy filtering expected on `assigned_employee_id`, `status`, and `scheduled_date`. Use composite indexes.
*   Enforce referential integrity to `bookings` and `employees`.

## RabbitMQ Events
*   `WorkOrderAssignedEvent` -> Triggers push notification to technician.
*   `WorkOrderCompletedEvent` -> Triggers review of parent Booking status (possibly marking Booking as COMPLETED).

## Validation Checklist
- [ ] Can a Work Order be linked to an AMC schedule?
- [ ] Is the state machine robust against invalid transitions?
- [ ] Is technician rejection handled gracefully (back to pool)?

## Common Mistakes
*   Putting pricing information in the Work Order.
*   Assuming a 1:1 mapping with Service Visit (a job spanning multiple days needs multiple visits).

## Related Skills
- `domain/booking`
- `domain/service-visit`
