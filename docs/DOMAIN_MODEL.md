# Domain Model Reference
**Architecture Baseline:** 2026.09 (V2.1.0)  
**Document Version:** 2.1.0  
**Implementation Status:** Documentation & Specification Baseline  
— Backend: Java 21 + Spring Boot 3.3.x Modular Monolith  
— System of Record: PostgreSQL 16  

This document defines the canonical domain model, aggregate boundaries, state machines, and business invariants across the Pest Control ERP system.

## 1. Domain Entities & Aggregate Boundaries

The domain model is partitioned into aggregates that align directly with the 18 domain modules defined in [`docs/MODULE_CATALOG.md`](MODULE_CATALOG.md):

- **Booking Aggregate (`bookings` module)**: `bookings`, `booking_items`, `booking_events`, `coupons`, `coupon_redemptions`, `availability_slots`.
- **Dispatch Aggregate (`dispatch` module)**: `work_orders` (1:N `service_visits`), `service_checklists`, `offline_sync_logs`, `sync_conflicts`.
- **Payment Aggregate (`payments` module)**:
  - `payments`: Authoritative ERP-level financial aggregate.
  - `payment_transactions`: Gateway-level monetary movements (charges, refunds, transfers).
  - `payment_events`: Immutable incoming webhook audit observations.
  - `invoices`, `invoice_items`: Sequential billing records and line item breakdowns.
- **Inventory Aggregate (`inventory` module)**: `chemical_products`, `chemical_batches`, `inventory_locations`, `inventory_transactions`, `service_material_usage`.
- **AMC Aggregate (`amc` module)**: `amc_contracts`, `amc_schedules`.
- **Catalog Aggregate (`catalog` module)**: `service_categories`, `services`, `pricing_rules`, `pricing_tiers`.
- **Customer Aggregate (`customers` module)**: `customers`, `customer_addresses`.
- **Employee Aggregate (`employees` module)**: `employees` (core staff identity with role enum `TECHNICIAN`, `DISPATCHER`, `AGENCY_MANAGER`, `ACCOUNTANT`), `skills`, `employee_skills`.
- **Agency Aggregate (`agencies` module)**: `agencies` (tenancy model using `agency_id`), `agency_service_areas`.
- **Expense Aggregate (`expenses` module)**: `expenses`, `expense_categories`.
- **Support Aggregate (`support` module)**: `support_tickets`, `support_messages`, `service_ratings`.
- **Cross-Cutting Foundation Modules**: `auth`, `users`, `notifications`, `files`, `reporting`, `audit`, `outbox`.

---

## 2. State Machines & Lifecycle Rules

### 1. Booking Status (Commercial Aggregate State)
**Lifecycle**: `PENDING` $\rightarrow$ `CONFIRMED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED` $\rightarrow$ `CLOSED` (or `CANCELLED`).

- **`PENDING`**: Initial checkout. Awaiting slot lock and (for prepaid) gateway payment authorization.
- **`CONFIRMED`**: Slot capacity locked in PostgreSQL (`booked_count++`). For COD: `payment_status = 'PENDING'` is valid. For Prepaid: `payment_status` is `AUTHORIZED` or `PAID`. Work Order generated.
- **`IN_PROGRESS`**: **Derived business state.** Set when any child Work Order / Service Visit is actively underway (`ACCEPTED`, `ON_THE_WAY`, `ARRIVED`, `STARTED`) or when an initial visit is completed while subsequent scheduled visits/work orders remain open.
- **`COMPLETED`**: **Derived business state.** Set when ALL operational Work Orders associated with the booking have reached `COMPLETED` (or `CANCELLED`), all child Service Visits are terminal (`COMPLETED` or `CANCELLED`), and no operational work remains open.
- **`CLOSED`**: Set when operational status is `COMPLETED` **AND** financial settlement is resolved (`payment_status = 'PAID'` or COD handover verified) **AND** final sequential PDF invoice is generated and linked.
- **`CANCELLED`**: Cancelled prior to operational completion. Slot capacity released (`booked_count--`). Child Work Orders and Visits cancelled. Refund issued if prepaid.

### 2. Work Order Status (Operational Dispatch State)
**Lifecycle**: `ASSIGNED` $\rightarrow$ `ACCEPTED` $\rightarrow$ `REJECTED` $\rightarrow$ `ON_THE_WAY` $\rightarrow$ `ARRIVED` $\rightarrow$ `STARTED` $\rightarrow$ `COMPLETED` (or `CANCELLED`).
- Owned exclusively by the `dispatch` module.
- Represents the operational grouping of work dispatched to a technician.

### 3. Service Visit Status (Field Execution State)
**Lifecycle**: `SCHEDULED` $\rightarrow$ `ON_THE_WAY` $\rightarrow$ `ARRIVED` $\rightarrow$ `STARTED` $\rightarrow$ `COMPLETED` (or `FAILED` | `CANCELLED`).
- Cardinality: 1 Work Order to N Service Visits (1:N). Supports failed visits, rescheduled revisits, warranty inspections, and multi-technician visits.
- **`FAILED`**: Treatment attempted but blocked on-site (access denied, customer absent). Creates a NEW child `ServiceVisit` on the SAME Work Order.
- **`COMPLETED`**: Service executed successfully. Executes **transactional inventory deduction** in the same PostgreSQL transaction with `SELECT ... FOR UPDATE` on `chemical_batches`, writes `service_material_usage`, and inserts `outbox_events(ServiceVisitCompleted)`.

### 4. Payment Status (Financial Settlement State)
**Lifecycle**: `PENDING` $\rightarrow$ `AUTHORIZED` $\rightarrow$ `PAID` | `PARTIAL` | `FAILED`.  
**Reversals**: `PAID` | `PARTIAL` $\rightarrow$ `REFUNDED` | `PARTIALLY_REFUNDED`.
- Authoritative state machine updated exclusively by the server webhook processor via `payment_events (provider, gateway_event_id)` deduplication.

---

## 3. Canonical Booking-to-Technician Progression

The platform enforces a strict decouple-by-design progression from commercial commitment to physical technician assignment:

```text
1. Customer Booking Checkout
       │ (Selects Service, Address, Date & Time Window)
       ▼
2. Atomic Slot Reservation (PostgreSQL SELECT FOR UPDATE)
       │ (Reserves 1 unit from Agency Capacity Pool: availability_slots)
       ▼
3. Booking Confirmation (Commercial Status -> CONFIRMED)
       │ (Emits outbox event: BookingConfirmed)
       ▼
4. Operational Work Order Creation (Status -> ASSIGNED)
       │ (Dispatcher reviews board and assigns qualified Technician)
       ▼
5. Service Visit Scheduling (Status -> SCHEDULED)
       │ (Technician accepts job in mobile app; transitions to ACCEPTED -> ON_THE_WAY)
       ▼
6. Physical Execution & Completion (Status -> STARTED -> COMPLETED)
       │ (Pessimistic inventory deduction + customer signature + outbox event ServiceVisitCompleted)
       ▼
7. Financial Settlement & Invoicing (Payment -> PAID, Booking -> CLOSED)
```

---

## 4. Business Invariants

1. **Transactional Slot Capacity**: A booking can only transition to `CONFIRMED` if slot capacity is available in PostgreSQL and locked via `SELECT ... FOR UPDATE`.
2. **Transactional Inventory Deductions**: Inventory deduction runs strictly inside the service visit completion transaction with row locks on `chemical_batches` (`CHECK (current_quantity_available >= 0)`). RabbitMQ is never used to trigger deductions.
3. **Outbox Pattern Publication**: No business transaction may publish directly to RabbitMQ. Domain events are inserted into `outbox_events` in the same database transaction as the business mutation.
4. **Authoritative Webhook Deduplication**: Webhook event processing relies solely on the unique constraint `(provider, gateway_event_id)` in `payment_events`.
5. **Technician Concurrency & Single Active Device**: A technician cannot accept or start a new job if they currently have another active job in `STARTED` status. Each technician is restricted to exactly ONE active registered device.
6. **Immutable Invoices**: Invoice numbers from the PostgreSQL sequence (`INV-YYYY-NNNNN`) and invoice PDF documents are strictly immutable once issued.
7. **Append-Only Audit Logs**: Rows in `audit_logs` can NEVER be updated or deleted. Enforced by database trigger.

---

## 5. Cardinality Summary Table

| Relationship | Cardinality | Foreign Key | Delete Rule |
| :--- | :--- | :--- | :--- |
| customers → bookings | 1:N | `customer_id` | RESTRICT |
| bookings → booking_items | 1:N | `booking_id` | CASCADE |
| bookings → work_orders | 1:N | `booking_id` | RESTRICT |
| work_orders → service_visits | 1:N | `work_order_id` | RESTRICT |
| service_visits → service_material_usage | 1:N | `service_visit_id` | RESTRICT |
| chemical_batches → service_material_usage | 1:N | `chemical_batch_id` | RESTRICT |
| payments → payment_events | 1:N | `payment_id` | RESTRICT |
| payments → payment_transactions | 1:N | `payment_id` | RESTRICT |
| bookings → payments | 1:N | `booking_id` | RESTRICT |
| coupons → coupon_redemptions | 1:N | `coupon_id` | RESTRICT |
| customers → coupon_redemptions | 1:N | `customer_id` | RESTRICT |
| amc_contracts → amc_schedules | 1:N | `amc_contract_id` | RESTRICT |
| dispatch → sync_conflicts | 1:N | `agency_id` | RESTRICT |
`amc_contract_id` | RESTRICT |
