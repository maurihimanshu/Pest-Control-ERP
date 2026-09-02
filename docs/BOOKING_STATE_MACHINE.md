# State Machine Specification
## Booking Aggregate Lifecycle, Work Order, Field Visit & Payment State Machines

**Architecture Baseline:** 2026.09 (V2.1.0)  
**Document Version:** 2.1.0  
**Enforcement Layer:** Spring Boot Domain Services & PostgreSQL Enums/Constraints  
**Reference:** [`docs/DOMAIN_MODEL.md`](DOMAIN_MODEL.md), [`docs/CONCURRENCY_AND_IDEMPOTENCY.md`](CONCURRENCY_AND_IDEMPOTENCY.md)  
**Date:** September 2026  

---

## 1. Domain Lifecycle Architecture

To support multi-visit treatments, warranty follow-ups, and recurring AMC contracts without data loss or tight coupling, the platform maintains **four synchronized state machines**:

```text
┌────────────────────────────────────────┐     ┌────────────────────────────────────────┐
│             Booking Status             │     │           Work Order Status            │
│       (Commercial Aggregate State)     │     │         (Operational Dispatch)         │
├────────────────────────────────────────┤     ├────────────────────────────────────────┤
│ • PENDING                              │     │ • ASSIGNED                             │
│ • CONFIRMED                            │     │ • ACCEPTED                             │
│ • IN_PROGRESS                          │     │ • REJECTED                             │
│ • COMPLETED                            │     │ • ON_THE_WAY                           │
│ • CLOSED                               │     │ • ARRIVED                              │
│ • CANCELLED                            │     │ • STARTED                              │
│                                        │     │ • COMPLETED                            │
│                                        │     │ • CANCELLED                            │
└────────────────────────────────────────┘     └────────────────────────────────────────┘

┌────────────────────────────────────────┐     ┌────────────────────────────────────────┐
│          Service Visit Status          │     │             Payment Status             │
│           (Field Execution)            │     │         (Financial Settlement)         │
├────────────────────────────────────────┤     ├────────────────────────────────────────┤
│ • SCHEDULED                            │     │ • PENDING                              │
│ • ON_THE_WAY                           │     │ • AUTHORIZED                           │
│ • ARRIVED                              │     │ • PAID                                 │
│ • STARTED                              │     │ • PARTIAL                              │
│ • COMPLETED                            │     │ • FAILED                               │
│ • FAILED                               │     │ • REFUNDED                             │
│ • CANCELLED                            │     │ • PARTIALLY_REFUNDED                   │
└────────────────────────────────────────┘     └────────────────────────────────────────┘
```

---

## 2. Commercial Booking Aggregate State Machine

### 2.1 Derived Aggregate State Concept
A `Booking` is the top-level commercial agreement. Its status is not a simple manual toggle; rather, while progressing through execution, **it acts as a derived business aggregate state** reflecting the collective progress of its child Work Orders, Service Visits, and Payment transactions.

```text
       [ Customer Checkout ]
                 │
                 ▼
          ┌─────────────┐
          │   PENDING   │
          └──────┬──────┘
                 │ (Payment Verified OR Cash-on-Delivery Slot Confirmed)
                 ▼
          ┌─────────────┐
          │  CONFIRMED  │◄─────────────────────────────┐
          └──────┬──────┘                              │ (Reschedule / Reopen)
                 │ (Any child WO/Visit becomes Active) │
                 ▼                                     │
          ┌─────────────┐                              │
          │ IN_PROGRESS │──────────────────────────────┘
          └──────┬──────┘
                 │ (ALL Child Work Orders COMPLETED & all Visits Terminal)
                 ▼
          ┌─────────────┐
          │  COMPLETED  │ (Operational work done, awaiting financial settlement)
          └──────┬──────┘
                 │ (Payment = PAID/Reconciled AND Final Invoice Issued)
                 ▼
          ┌─────────────┐
          │   CLOSED    │ (Fully archived commercial contract)
          └─────────────┘
                 ▲
                 │ (Cancelled before visit start)
          ┌──────┴──────┐
          │  CANCELLED  │
          └─────────────┘
```

### 2.2 Formal State Aggregation Logic & Matrix

| Booking Status | Exact Preconditions & Deterministic Aggregation Rule | Permitted Triggers / Actions |
|:---|:---|:---|
| **`PENDING`** | Booking created by customer/admin. Slot lock or payment authorization is pending. | Cart checkout initiated; Redis slot pre-lock active. |
| **`CONFIRMED`** | Slot capacity reserved in PostgreSQL (`booked_count++`). For Prepaid: `payment_status` is `AUTHORIZED` or `PAID`. For COD: `payment_status = 'PENDING'` is valid. Initial Work Order generated in `ASSIGNED` status. | System/Webhook confirms slot & payment mode; emits `BookingConfirmed`. |
| **`IN_PROGRESS`** | At least one child Work Order is `ACCEPTED`, `ON_THE_WAY`, `ARRIVED`, `STARTED`, or has a Service Visit in progress. OR: An initial Work Order/Visit is `COMPLETED`, but secondary scheduled Work Orders (e.g. warranty visit, subsequent AMC visit) remain open/scheduled. | Field tech accepts/starts visit; updates booking to reflect active operations. |
| **`COMPLETED`** | **ALL** operational child Work Orders associated with the booking have reached terminal `COMPLETED` (or `CANCELLED` if non-essential), all child Service Visits are terminal (`COMPLETED` / `CANCELLED`), and NO open/active operational work orders remain. | System detects last open Work Order transition to `COMPLETED`; emits `BookingCompleted`. |
| **`CLOSED`** | Booking operational status is `COMPLETED` **AND** financial settlement is fully resolved (`payment_status = 'PAID'` or COD cash handover verified) **AND** final sequential PDF invoice is generated and linked. | Accountant reconciles or system completes invoice upload; emits `BookingClosed`. |
| **`CANCELLED`** | Booking cancelled prior to operational completion. Slot capacity is released (`booked_count--`). Child Work Orders and Visits are marked `CANCELLED`. If prepaid, gateway refund is initiated (`REFUNDED`). | Customer or Admin cancellation before service execution starts. |

---

## 3. Operational Work Order State Machine (`WorkOrderStatus`)

Owned by the `dispatch` module. Represents the administrative dispatch grouping for a service assignment.

```text
          ┌─────────────┐
          │  ASSIGNED   │
          └──────┬──────┘
                 ├─────────────────────────────────────────┐
                 │ (Technician Accepts)                    │ (Technician Rejects within SLA)
                 ▼                                         ▼
          ┌─────────────┐                           ┌─────────────┐
          │  ACCEPTED   │                           │  REJECTED   │ (Returns to dispatch board)
          └──────┬──────┘                           └─────────────┘
                 │ (En Route to site)
                 ▼
          ┌─────────────┐
          │ ON_THE_WAY  │
          └──────┬──────┘
                 │ (Arrived at customer location)
                 ▼
          ┌─────────────┐
          │   ARRIVED   │
          └──────┬──────┘
                 │ (Begins treatment)
                 ▼
          ┌─────────────┐
          │   STARTED   │
          └──────┬──────┘
                 │ (All assigned Service Visits COMPLETED)
                 ▼
          ┌─────────────┐
          │  COMPLETED  │
          └─────────────┘
```

---

## 4. Field Service Visit State Machine (`ServiceVisitStatus`)

Owned by the `dispatch` module. Represents the physical field execution event on-site (1:N cardinality with Work Order).

| From Status | To Status | Actor | API Endpoint | Trigger & Side Effects |
|:---|:---|:---|:---|:---|
| *(None)* | `SCHEDULED` | Dispatcher / System | `POST .../work-orders/{id}/schedule-visit` | Created with target date, time slot, and technician. |
| `SCHEDULED` | `ON_THE_WAY` | Field Technician | `POST .../visits/{id}/on-the-way` | Tech en route; emits push notification to customer. |
| `ON_THE_WAY` | `ARRIVED` | Field Technician | `POST .../visits/{id}/arrived` | Captures GPS coordinates & arrival timestamp. |
| `ARRIVED` | `STARTED` | Field Technician | `POST .../visits/{id}/start` | Captures pre-treatment photos & begins treatment. |
| `STARTED` | `COMPLETED` | Field Technician | `POST .../visits/{id}/complete` | **Transactional:** Deducts chemical batch stock, writes material usage, captures post-photos & signature, writes `outbox_events(ServiceVisitCompleted)`. |
| `STARTED` | `FAILED` | Field Technician / Admin | `POST .../visits/{id}/fail` | Service aborted (access denied, customer absent). Generates a NEW child `ServiceVisit` on the SAME Work Order for follow-up. |
| `SCHEDULED` | `CANCELLED` | Dispatcher / Admin | `POST .../visits/{id}/cancel` | Visit cancelled before travel starts. |

---

## 5. Authoritative Payment Settlement State Machine (`PaymentStatus`)

Managed exclusively by the backend in the `payments` module:

```text
                  ┌─────────────┐
                  │   PENDING   │
                  └──────┬──────┘
                         ├─────────────────────────────────────────┐
                         │ (Payment Authorized / Funds Held)       │ (Payment Failed)
                         ▼                                         ▼
                  ┌─────────────┐                           ┌─────────────┐
                  │ AUTHORIZED  │                           │   FAILED    │
                  └──────┬──────┘                           └─────────────┘
                         ├────────────────────────┐
                         │ (Capture Succeeded)    │ (Partial Payment / Split)
                         ▼                        ▼
                  ┌─────────────┐          ┌─────────────┐
                  │    PAID     │          │   PARTIAL   │
                  └──────┬──────┘          └──────┬──────┘
                         ├────────────────────────┤ (Remainder Paid)
                         │ (Partial Refund)       │
                         ▼                        │
               ┌──────────────────┐               │
               │PARTIALLY_REFUNDED│               │
               └─────────┬────────┘               │
                         │ (Full Refund Balance)  │
                         ▼                        │
               ┌──────────────────┐               │
               │     REFUNDED     │◄──────────────┘
               └──────────────────┘
```

### 5.1 Payment State Transition Matrix

| From Status | Allowed Target Statuses | Trigger / Event | Invalid / Forbidden Transitions |
|:---|:---|:---|:---|
| **`PENDING`** | `AUTHORIZED`, `PAID`, `PARTIAL`, `FAILED` | Gateway authorization, instant capture, or gateway decline | `REFUNDED`, `PARTIALLY_REFUNDED` |
| **`AUTHORIZED`** | `PAID`, `FAILED`, `CANCELLED` | Capture confirmation or auth expiration | `REFUNDED`, `PENDING` |
| **`PARTIAL`** | `PAID`, `FAILED`, `PARTIALLY_REFUNDED` | Subsequent installment payment or partial dispute | `AUTHORIZED`, `PENDING` |
| **`PAID`** | `PARTIALLY_REFUNDED`, `REFUNDED` | Customer refund or service dispute | `PENDING`, `AUTHORIZED`, `FAILED`, `PARTIAL` |
| **`PARTIALLY_REFUNDED`** | `REFUNDED` | Remaining balance refunded | `PAID`, `PENDING`, `AUTHORIZED`, `FAILED` |
| **`FAILED`** | `PENDING` (Retry checkout only) | Customer reinitiates checkout with new payment attempt | `PAID`, `REFUNDED`, `AUTHORIZED` |
| **`REFUNDED`** | *(Terminal)* | None | Any transition (Terminal State) |


---

## 6. Multi-Order & Multi-Visit Aggregation Scenarios

### Scenario A: Single Service with Rescheduled/Failed Visit
1. Customer books Cockroach Control $\rightarrow$ Booking `CONFIRMED`, WO1 `ASSIGNED`, SV1 `SCHEDULED`.
2. Tech arrives, customer not home $\rightarrow$ SV1 transitions to `FAILED`.
3. Dispatcher schedules SV2 for next day under WO1 $\rightarrow$ Booking remains `IN_PROGRESS`.
4. Tech executes SV2 successfully $\rightarrow$ SV2 transitions to `COMPLETED`.
5. WO1 transitions to `COMPLETED` $\rightarrow$ Booking transitions to `COMPLETED` $\rightarrow$ After payment & invoice, Booking transitions to `CLOSED`.

### Scenario B: Multi-Work Order Treatment (Initial + Warranty Follow-up)
1. Customer books Termite Treatment with 90-day warranty $\rightarrow$ Booking `CONFIRMED`.
2. WO1 (Initial Treatment) executes: SV1 `COMPLETED` $\rightarrow$ WO1 `COMPLETED`.
3. Customer reports pest resurgence on Day 45 $\rightarrow$ Admin approves warranty claim and generates WO2 (`WARRANTY_VISIT`) linked to original Booking.
4. Booking immediately re-evaluates to `IN_PROGRESS` while WO2 is open.
5. Tech executes SV2 for WO2 $\rightarrow$ WO2 `COMPLETED`.
6. ALL Work Orders (WO1, WO2) are now `COMPLETED` $\rightarrow$ Booking transitions to `COMPLETED` (and `CLOSED`).
