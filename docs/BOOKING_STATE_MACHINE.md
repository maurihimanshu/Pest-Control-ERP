# State Machine Specification
## Booking, Work Order, Field Visit & Payment Lifecycles

**Document Version:** 1.0.0  
**Enforcement Layer:** Spring Boot Domain Services & PostgreSQL Enums/Constraints  
**Date:** September 2026  

---

## 1. Domain Lifecycle Separation

To prevent tight coupling and accommodate multi-visit treatments, warranty revisits, and AMC contracts, the system maintains **four independent, synchronized state machines**:

```text
┌─────────────────────────┐     ┌─────────────────────────┐
│     Booking Status      │     │    Work Order Status    │
│  (Commercial Contract)  │     │  (Operational Dispatch) │
├─────────────────────────┤     ├─────────────────────────┤
│ • PENDING               │     │ • UNASSIGNED            │
│ • CONFIRMED             │     │ • ASSIGNED              │
│ • CANCELLED             │     │ • IN_PROGRESS           │
│ • CLOSED                │     │ • COMPLETED             │
│                         │     │ • CANCELLED             │
└─────────────────────────┘     └─────────────────────────┘

┌─────────────────────────┐     ┌─────────────────────────┐
│  Service Visit Status   │     │     Payment Status      │
│    (Field Execution)    │     │  (Financial Settlement) │
├─────────────────────────┤     ├─────────────────────────┤
│ • SCHEDULED             │     │ • PENDING               │
│ • ACCEPTED              │     │ • AUTHORIZED            │
│ • REJECTED              │     │ • PAID                  │
│ • ON_THE_WAY            │     │ • PARTIAL               │
│ • ARRIVED               │     │ • FAILED                │
│ • STARTED               │     │ • REFUNDED              │
│ • COMPLETED             │     │ • PARTIALLY_REFUNDED    │
└─────────────────────────┘     └─────────────────────────┘
```

---

## 2. Commercial Booking State Machine

```text
       [ Customer Checkout ]
                 │
                 ▼
          ┌─────────────┐
          │   PENDING   │
          └──────┬──────┘
                 │ (Payment Success OR Cash-on-Delivery Selected)
                 ▼
          ┌─────────────┐
          │  CONFIRMED  │◄─────────────────────────────┐
          └──────┬──────┘                              │ (Reschedule)
                 │ (All Work Orders Completed)         │
                 ▼                                     │
          ┌─────────────┐                       ┌──────┴──────┐
          │   CLOSED    │                       │ RESCHEDULED │
          └─────────────┘                       └─────────────┘
                 ▲                                     ▲
                 │ (Cancelled before visit start)      │
          ┌──────┴──────┐                              │
          │  CANCELLED  │──────────────────────────────┘
          └─────────────┘
```

### Transition Matrix:

| Current State | Target State | Trigger Event | Allowed Actor | Side Effects & Actions |
| :--- | :--- | :--- | :--- | :--- |
| `[None]` | `PENDING` | Customer initiates cart checkout | Customer | Slot reserved in Redis (5 min lock) |
| `PENDING` | `CONFIRMED` | Payment captured / COD selected | System / Gateway | Generates `WorkOrder`, publishes `booking.confirmed` |
| `PENDING` | `CANCELLED` | Payment timeout / User abort | System / Customer | Releases Redis slot lock |
| `CONFIRMED` | `CANCELLED` | Customer / Admin cancels | Customer / Admin | Cancels Work Orders, triggers refund if paid |
| `CONFIRMED` | `CLOSED` | Final Service Visit completed | System | Generates invoice, sends review prompt |

> **CONFIRMED + PENDING payment is valid:** For COD and deferred-payment bookings, CONFIRMED status means the business has accepted the booking and locked the slot. paymentStatus = PENDING is acceptable and expected until COD collection at service completion.
>
> **Prepaid bookings:** CONFIRMED is only set after backend-verified payment authorization. The confirmation flow is determined by the booking_type field.

---

## 3. Service Visit Status State Machine (ServiceVisitStatus)

Owned by: ServiceVisit entity (child of WorkOrder)
One WorkOrder may have MULTIPLE ServiceVisits (1:N cardinality).

| From Status | To Status | Actor | API Endpoint | Trigger |
|:---|:---|:---|:---|:---|
| (created) | SCHEDULED | System | POST /api/v1/dispatch/work-orders/{id}/schedule-visit | WorkOrder assigned |
| SCHEDULED | ON_THE_WAY | Technician | POST /api/v1/dispatch/visits/{id}/on-the-way | Tech starts traveling |
| ON_THE_WAY | ARRIVED | Technician | POST /api/v1/dispatch/visits/{id}/arrived | Tech at location |
| ARRIVED | STARTED | Technician | POST /api/v1/dispatch/visits/{id}/start | Service begins |
| STARTED | COMPLETED | Technician | POST /api/v1/dispatch/visits/{id}/complete | All checklist done |
| SCHEDULED | CANCELLED | DISPATCHER/ADMIN | POST /api/v1/dispatch/visits/{id}/cancel | Before visit starts |
| STARTED | FAILED | Technician/ADMIN | POST /api/v1/dispatch/visits/{id}/fail | Cannot complete visit |

### FAILED vs CANCELLED
- FAILED: Service was attempted but could not be completed (customer not home, equipment failure, access denied). Creates a NEW ServiceVisit on the SAME WorkOrder for rescheduling.
- CANCELLED: Visit cancelled before it started. May trigger booking reschedule or work order cancellation.

### Side Effects of COMPLETED
1. ServiceCompleted event → outbox_events
2. Inventory deduction (transactional, PostgreSQL FOR UPDATE)
3. COGS calculation
4. Triggers InvoiceService (if payment complete) or marks booking IN_PROGRESS
5. audit_log entry

---

## 4. Payment Settlement State Machine

```text
          ┌─────────────┐
          │   PENDING   │
          └──────┬──────┘
                 ├─────────────────────────────────────────┐
                 │ (Gateway Webhook: Success)              │ (Gateway: Failed)
                 ▼                                         ▼
          ┌─────────────┐                           ┌─────────────┐
          │    PAID     │                           │   FAILED    │
          └──────┬──────┘                           └─────────────┘
                 ├────────────────────────┐
                 │ (Partial Refund)       │ (Full Refund)
                 ▼                        ▼
       ┌──────────────────┐      ┌─────────────────┐
       │PARTIALLY_REFUNDED│      │    REFUNDED     │
       └──────────────────┘      └─────────────────┘
```

---

## 5. Conflict Resolution & Transition Guards

1. **Strict Forward-Only Progression:** State transitions must follow defined directed acyclic paths. Attempts to jump illegal states (e.g. `SCHEDULED` $\rightarrow$ `COMPLETED`) result in HTTP `409 Conflict` (`INVALID_STATE_TRANSITION`).
2. **Technician Identity Guard:** State transitions for a Service Visit require the calling user to match `primary_employee_id` or possess `SUPER_ADMIN` authority.
3. **Database Transaction Lock:** Status updates run inside a `SELECT ... FOR UPDATE` pessimistic lock or version-based optimistic lock (`@Version` on JPA Entity).

---

*This state machine is enforced by Spring State Machine / Domain Services in the backend.*
