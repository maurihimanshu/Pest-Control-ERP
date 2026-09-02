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
│ • ASSIGNED                             │     │ • REJECTED                             │
│ • IN_PROGRESS                          │     │ • ON_THE_WAY                           │
│ • COMPLETED                            │     │ • ARRIVED                              │
│ • CLOSED                               │     │ • STARTED                              │
│ • CANCELLED                            │     │ • COMPLETED                            │
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

### 2.1 Derived Aggregate State Concept & Lifecycle Progression
A `Booking` is the top-level commercial agreement. Its status is not an arbitrary manual toggle; rather, it progresses through execution as a derived business aggregate state reflecting the collective progress of its child Work Orders, Service Visits, and Payment transactions:

```text
       [ Customer Checkout ]
                 │
                 ▼
          ┌─────────────┐
          │   PENDING   │───────┐
          └──────┬──────┘       │ (Pre-confirmation cancel)
                 │              ▼
                 │ (Slot Locked & Payment Authorized / COD Confirmed)
                 ▼
          ┌─────────────┐
          │  CONFIRMED  │───────┐
          └──────┬──────┘       │ (Pre-dispatch cancel)
                 │              ▼
                 │ (Technician Assigned by Dispatcher / Auto-Dispatch)
                 ▼
          ┌─────────────┐
          │  ASSIGNED   │───────► ┌─────────────┐
          └──────┬──────┘         │  CANCELLED  │
                 │                └─────────────┘
                 │ (Technician En Route / Visit In Progress)
                 ▼
          ┌─────────────┐
          │ IN_PROGRESS │  <── (Execution exceptions spawn new child ServiceVisits,
          └──────┬──────┘          NOT booking cancellation)
                 │
                 │ (ALL Child Work Orders COMPLETED & all Visits Terminal)
                 ▼
          ┌─────────────┐
          │  COMPLETED  │ (Operational work done, awaiting financial settlement)
          └──────┬──────┘
                 │
                 │ (Payment = PAID/Reconciled AND Final Sequential Invoice Linked)
                 ▼
          ┌─────────────┐
          │   CLOSED    │ (Fully archived commercial contract)
          └─────────────┘
```

### 2.2 Strict Invariants on Cancellation, Rescheduling & Reversals

1. **Cancellation Window Invariant:**
   - Cancellation is ONLY permitted prior to physical service execution: `PENDING → CANCELLED`, `CONFIRMED → CANCELLED`, or `ASSIGNED → CANCELLED`.
   - Once a technician is en route / arrived / started (`IN_PROGRESS`), the booking CANNOT be directly cancelled.
   - **`COMPLETED → CANCELLED` IS STRICTLY FORBIDDEN.**
2. **Post-Completion Adjustments & Reversals:**
   - Completed work that must be financially reversed (e.g. customer dissatisfaction, service dispute) is handled via a **Billing Adjustment / Credit Note and Refund Workflow** (`payments.status → PARTIALLY_REFUNDED | REFUNDED`, `invoices.status → ADJUSTED | CREDIT_NOTE`), NEVER by altering the historical booking status to `CANCELLED`.
3. **Rescheduling as an Operational Mutation:**
   - Rescheduling is NOT a terminal lifecycle state. When a customer or dispatcher reschedules an appointment, the system executes an atomic slot release and re-reservation on `availability_slots`, updates the target date/time on the active `WorkOrder` / `ServiceVisit`, and maintains the booking in `CONFIRMED` or `ASSIGNED`.
4. **Visit Exceptions do NOT Cancel the Booking:**
   - If a technician arrives and the customer is absent (`ServiceVisitStatus = FAILED`), the `Booking` remains `IN_PROGRESS`. Dispatch schedules a follow-up `ServiceVisit` under the existing `WorkOrder`.

### 2.3 Formal State Aggregation Logic & Matrix

| Booking Status | Exact Preconditions & Deterministic Aggregation Rule | Permitted Triggers / Actions |
|:---|:---|:---|
| **`PENDING`** | Booking created by customer/admin. Slot lock or payment authorization is pending. | Cart checkout initiated; Redis slot pre-lock active. Permitted: `→ CONFIRMED`, `→ CANCELLED`. |
| **`CONFIRMED`** | Slot capacity reserved in PostgreSQL (`booked_count++`). For Prepaid: `payment_status` is `AUTHORIZED` or `PAID`. For COD: `payment_status = 'PENDING'` is valid. Initial Work Order generated. | System/Webhook confirms slot & payment mode; emits `BookingConfirmed`. Permitted: `→ ASSIGNED`, `→ CANCELLED`. |
| **`ASSIGNED`** | Dispatcher or auto-dispatch has assigned a qualified technician. Work order is in `ASSIGNED` or `ACCEPTED` status. | Dispatch assignment complete; emits `TechnicianAssigned`. Permitted: `→ IN_PROGRESS`, `→ CANCELLED`. |
| **`IN_PROGRESS`** | Technician is en route, arrived, or actively performing treatment (`ON_THE_WAY`, `ARRIVED`, `STARTED`). OR: Initial visit complete while subsequent warranty/AMC visits remain open. | Field tech starts travel/treatment; updates booking to active. Permitted: `→ COMPLETED`. |
| **`COMPLETED`** | **ALL** operational child Work Orders associated with the booking have reached terminal `COMPLETED` (or non-essential sub-orders `CANCELLED`), all child Service Visits are terminal (`COMPLETED` / `CANCELLED`), and NO open operational work remains. | System detects last open Work Order transition to `COMPLETED`; emits `BookingCompleted`. Permitted: `→ CLOSED`. |
| **`CLOSED`** | Booking operational status is `COMPLETED` **AND** financial settlement is fully resolved (`payment_status = 'PAID'` or COD cash handover verified) **AND** final sequential PDF invoice is generated and linked. | Accountant reconciles or system completes invoice upload; emits `BookingClosed`. Terminal state. |
| **`CANCELLED`** | Booking cancelled prior to physical execution start. Slot capacity is released (`booked_count--`). Child Work Orders and Visits are marked `CANCELLED`. If prepaid, gateway refund is initiated (`REFUNDED`). | Customer or Admin cancellation before service travel/execution starts. Terminal state. |

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

---

## 7. Cross-Aggregate State Invariant Matrix (P0-04)

The platform enforces strict simultaneous state legality across domain aggregates:

| Booking Status | Legal WorkOrder States | Legal ServiceVisit States | Legal Payment States | Strictly Forbidden Combinations / Invariants |
| :--- | :--- | :--- | :--- | :--- |
| **`PENDING`** | *(None created)* | *(None created)* | `PENDING`, `AUTHORIZED`, `FAILED` | Cannot have Work Orders or Service Visits. Cannot be `PAID`. |
| **`CONFIRMED`** | `ASSIGNED` | `SCHEDULED` | `PENDING` (COD), `AUTHORIZED`, `PAID` | Cannot have visits in `STARTED` or `COMPLETED`. Cannot have `FAILED` payments unless COD. |
| **`ASSIGNED`** | `ASSIGNED`, `ACCEPTED` | `SCHEDULED` | `PENDING` (COD), `AUTHORIZED`, `PAID` | Cannot have visits in `STARTED` or `COMPLETED`. |
| **`IN_PROGRESS`** | `ACCEPTED`, `ON_THE_WAY`, `ARRIVED`, `STARTED`, `COMPLETED` (if multi-order) | `ON_THE_WAY`, `ARRIVED`, `STARTED`, `FAILED`, `COMPLETED` (if other open) | `PENDING` (COD), `AUTHORIZED`, `PAID`, `PARTIAL` | Cannot be `CLOSED` or `CANCELLED`. Cannot have all child visits terminal without Booking progressing. |
| **`COMPLETED`** | All child WOs must be `COMPLETED` (or `CANCELLED`) | All child SVs must be `COMPLETED` (or `CANCELLED`) | `PENDING` (COD uncollected), `AUTHORIZED`, `PAID`, `PARTIAL` | **Strict Invariant:** Cannot have any active Work Order (`ASSIGNED`, `STARTED`) or active Visit (`ON_THE_WAY`, `STARTED`). |
| **`CLOSED`** | `COMPLETED` (or `CANCELLED`) | `COMPLETED` (or `CANCELLED`) | `PAID`, `REFUNDED`, `PARTIALLY_REFUNDED` | Cannot be `CLOSED` with `payment_status = 'PENDING'` (unless bad debt written off) or open work orders. |
| **`CANCELLED`** | `CANCELLED` (or None) | `CANCELLED` (or None) | `PENDING`, `REFUNDED`, `FAILED` | **Strict Invariant:** Cannot have any active or started Work Order/Visit. `COMPLETED → CANCELLED` is strictly impossible. |

---

## 8. Multi-Service Booking Capacity Semantics (P1-02)

To avoid ambiguity in slot reservation:
1. **Commercial Booking Item vs. Physical Resource Requirement:**
   - A commercial `Booking` may contain multiple service line items (e.g. *General Pest Control* + *Cockroach Gel Treatment*).
   - **Default Co-located Treatment:** When multiple services are booked for the **same customer address, same date, and same time window**, they represent a **single physical technician visit** and deduct **exactly 1 capacity unit** from the territorial Agency Capacity Pool.
   - **Multi-Visit Packages:** When a package explicitly defines multiple phased visits (e.g. *Termite Treatment Stage 1* on Day 0 and *Stage 2* on Day 15), each scheduled visit independently reserves **1 capacity unit** for its respective date and time slot upon scheduling.
2. **Skill & Resource Allocation:** The total estimated duration of all bundled items is aggregated to ensure technician availability spans the entire duration without overlap.

