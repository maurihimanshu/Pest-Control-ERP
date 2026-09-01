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
3. **State Machine:**
   `PENDING` -> `CONFIRMED` -> `ASSIGNED` -> `IN_PROGRESS` -> `COMPLETED`
   Valid alternative flows:
   `PENDING` -> `CANCELLED`
   `CONFIRMED` -> `CANCELLED`
   `ASSIGNED` -> `RESCHEDULED` -> (back to ASSIGNED)
   `COMPLETED` -> `CLOSED` (after accounting/invoice settled)

## Entity Structure
*   `id` UUID
*   `customer_id` UUID
*   `address_id` UUID
*   `service_ids` JSONB array or M2M join table
*   `status` VARCHAR
*   `subtotal` DECIMAL
*   `tax` DECIMAL
*   `discount` DECIMAL
*   `total_amount` DECIMAL
*   `preferred_schedule_date` TIMESTAMP
*   `created_at`, `updated_at`

## Spring Service Methods
*   `Booking createBooking(CreateBookingDto request)`
*   `Booking confirmBooking(UUID bookingId)`
*   `void cancelBooking(UUID bookingId, String reason)`
*   `Booking rescheduleBooking(UUID bookingId, LocalDateTime newDate)`

## API Endpoints
*   `POST /api/v1/bookings`
*   `GET /api/v1/bookings/{id}`
*   `PUT /api/v1/bookings/{id}/status`
*   `POST /api/v1/bookings/{id}/cancel`

## Database Considerations
*   Ensure audit logs capture all state transitions.
*   The status column should have a `CHECK` constraint validating the allowed states.

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
