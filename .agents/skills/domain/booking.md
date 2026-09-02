---
name: booking
description: Handling the Booking domain, representing customer service requests.
category: domain
triggers:
  - Create a new booking
  - Manage booking states
  - Build booking API
inputs:
  - Customer request details
outputs:
  - Booking service implementation
dependencies:
  - database/relational-modeling
related_skills:
  - domain/work-order
  - domain/payment
---

# Skill: Booking Domain

## Purpose
To manage the lifecycle of a `Booking`, which represents the commercial intent and financial agreement between the customer and the business for pest control services.

## When to Use / When NOT to Use
**Use When:** Designing customer checkout flows, AMC contracts creation, or processing initial service requests.
**NOT to Use:** For dispatching technicians or tracking on-site work execution. That is the realm of the `Work Order` and `Service Visit`.

## Required Context
The `Booking` is the root aggregate for a service request. It dictates what services are required, what price was agreed upon, and when the service should ideally happen.

## Domain Rules & Constraints
1. **Immutable Fields:** Once a Booking transitions to `CONFIRMED`, fields affecting the price (services selected, coupon used) or core terms become immutable. Any changes require either a cancellation and re-booking or a specialized change-order process that recalculates pricing.
2. **Relationship:** 1 Booking -> N Work Orders.
3. **Canonical State Machine (7 States):**
   `PENDING` -> `CONFIRMED` -> `ASSIGNED` -> `IN_PROGRESS` -> `COMPLETED` -> `CLOSED`
   - Cancellation is allowed ONLY prior to execution start: `PENDING` -> `CANCELLED`, `CONFIRMED` -> `CANCELLED`, `ASSIGNED` -> `CANCELLED`.
   - `COMPLETED -> CANCELLED` is strictly forbidden. Post-completion reversals use Credit Notes and Refund workflows.
   - Rescheduling is an atomic schedule update (`scheduled_date`, `time_slot`, `reschedule_count`); it is NOT a `BookingStatus`.
4. **Tenant Scoping:** Bookings assigned to an agency must always be loaded and mutated with tenant scope validation (`findBy...AndAgencyId` or customer ownership check).

## Entity Structure
*   `id` UUID
*   `customer_id` UUID
*   `customer_address_id` UUID
*   `agency_id` UUID (FK)
*   `status` VARCHAR (`CHECK (status IN ('PENDING', 'CONFIRMED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'CLOSED'))`)
*   `payment_status` VARCHAR
*   `subtotal_amount` NUMERIC(12, 2)
*   `discount_amount` NUMERIC(12, 2)
*   `tax_amount` NUMERIC(12, 2)
*   `total_payable_amount` NUMERIC(12, 2)
*   `scheduled_date` DATE
*   `scheduled_time_slot` VARCHAR
*   `created_at`, `updated_at`

## Spring Service Methods
*   `Booking createBooking(UUID customerId, CreateBookingDto request)`
*   `Booking confirmBooking(UUID bookingId)`
*   `void cancelBooking(UUID bookingId, String reason)`
*   `Booking rescheduleBooking(UUID bookingId, LocalDate newDate, String newTimeSlot)`

## API Endpoints
*   `POST /api/v1/bookings`
*   `GET /api/v1/bookings/{id}`
*   `POST /api/v1/bookings/{id}/confirm`
*   `POST /api/v1/bookings/{id}/cancel`
*   `POST /api/v1/bookings/{id}/reschedule`

## Database Considerations
*   Ensure audit logs capture all state transitions.
*   The status column has `CHECK (status IN ('PENDING', 'CONFIRMED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'CLOSED'))`.
*   Capacity allocation locks `availability_slots` with `SELECT ... FOR UPDATE`.


## RabbitMQ Events
*   `BookingCreatedEvent` -> Consumed by Notification Service (Customer Email/SMS).
*   `BookingConfirmedEvent` -> Consumed by Dispatch/Scheduling Service to generate Work Orders.

## Validation Checklist
- [ ] Is the state machine strictly enforced?
- [ ] Are financial fields locked after confirmation?
- [ ] Does it correctly map to Customer and Address entities?
- [ ] Are events published appropriately on state change?

## Common Mistakes
*   Mixing dispatch details (technician assigned, GPS) into the Booking table.
*   Allowing price changes after confirmation without a formal amendment process.

## Related Skills
- `domain/work-order`
- `domain/payment`
