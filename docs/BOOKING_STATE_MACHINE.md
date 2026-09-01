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

---

## 3. Field Service Visit State Machine

The Service Visit tracks physical technician execution on the ground:

```text
          ┌─────────────┐
          │  SCHEDULED  │
          └──────┬──────┘
                 │ (Technician accepts assignment)
                 ▼
          ┌─────────────┐         ┌────────────┐
          │  ACCEPTED   │────────►│  REJECTED  │──► (Triggers Re-dispatch)
          └──────┬──────┘         └────────────┘
                 │ (Technician clicks 'Start Navigation')
                 ▼
          ┌─────────────┐
          │ ON_THE_WAY  │
          └──────┬──────┘
                 │ (Technician arrives at customer GPS)
                 ▼
          ┌─────────────┐
          │   ARRIVED   │
          └──────┬──────┘
                 │ (Safety checklist verified & treatment started)
                 ▼
          ┌─────────────┐
          │   STARTED   │
          └──────┬──────┘
                 │ (Materials logged, photos captured, customer signs)
                 ▼
          ┌─────────────┐
          │  COMPLETED  │
          └─────────────┘
```

### Transition Matrix:

| Current State | Target State | Preconditions | Side Effects |
| :--- | :--- | :--- | :--- |
| `SCHEDULED` | `ACCEPTED` | Assigned technician clicks Accept in App | Emits `visit.accepted`, updates Work Order |
| `SCHEDULED` | `REJECTED` | Technician rejects with mandatory reason | Emits `visit.rejected`, alerts Dispatch Desk |
| `ACCEPTED` | `ON_THE_WAY` | Technician departs for location | Sends FCM alert to Customer: *"Technician en route"* |
| `ON_THE_WAY` | `ARRIVED` | Device GPS within 200m of customer pin | Captures `actual_arrival_time` |
| `ARRIVED` | `STARTED` | Pre-service checklist confirmed | Sets `actual_start_time` |
| `STARTED` | `COMPLETED` | Photos uploaded, chemicals logged, signature saved | Generates Invoice PDF, closes Work Order |

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
