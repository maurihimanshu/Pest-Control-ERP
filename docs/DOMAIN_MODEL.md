# Domain Model Reference
Implementation Status: Documentation / Architecture Baseline
— Backend: Not implemented
— Customer Android: Not implemented
— Technician Android: Not implemented
— Admin Web: Not implemented

This document defines the canonical domain model, aggregates, state machines, and business invariants for the Pest Control ERP system.

## 1. Entities & Aggregates

- **Booking Aggregate**: `bookings`, `booking_items`, `booking_events`, `coupons`, `coupon_redemptions`
- **Dispatch Aggregate**: `work_orders` (1:N `service_visits`), `service_checklists`, `service_material_usage`
- **Payment Aggregate**: `payments`, `payment_events`, `invoices`, `invoice_items`
- **Inventory Aggregate**: `chemical_products`, `chemical_batches`, `inventory_locations`, `inventory_transactions`
- **AMC Aggregate**: `amc_contracts`, `amc_schedules`
- **Customer Aggregate**: `customers`, `customer_addresses`
- **Employee Aggregate**: `employees`, `employee_skills`
- **Agency Aggregate**: `agencies`
- **Support Aggregate**: `support_tickets`, `support_messages`
- **Cross-Cutting**: `notifications`, `file_metadata`, `audit_logs`, `outbox_events`

## 2. State Machines

### 1. BookingStatus
**Transitions**: PENDING → CONFIRMED → ASSIGNED → IN_PROGRESS → COMPLETED → CANCELLED | RESCHEDULED | CLOSED

- **PENDING**: Created by customer. Actor: Customer. API: `POST /api/v1/bookings`
- **CONFIRMED**: Backend validates service/slot. Actor: System (after slot lock). Side-effect: `availability_slot.booked_count++`, `BookingConfirmed` event.
- **ASSIGNED**: Dispatcher assigns technician. Actor: DISPATCHER/ADMIN. API: `POST /api/v1/dispatch/work-orders/assign`. Side-effect: creates WorkOrder, `WorkOrderCreated` event.
- **IN_PROGRESS**: Technician arrives and starts. Actor: System (derived from WorkOrder state). Side-effect: Booking status reflects field activity.
- **COMPLETED**: Service visit(s) completed & payment resolved. Actor: System. Side-effect: `BookingCompleted` event, invoice finalized.
- **CANCELLED**: Cancelled before completion. Actor: Customer / ADMIN / DISPATCHER. Side-effect: `availability_slot.booked_count--`, refund if paid.
- **RESCHEDULED**: New slot requested. Actor: Customer/ADMIN. Side-effect: old slot released, new slot locked.
- **CLOSED**: Final administrative close. Actor: ADMIN/SUPER_ADMIN.

*Payment Dependency Notes:*
- **COD / Deferred Payment**: `CONFIRMED` status does NOT require prior payment. `paymentStatus = PENDING` is valid. `CONFIRMED` means the backend has accepted the booking, locked the slot, and the service will proceed.
- **Prepaid**: `CONFIRMED` requires backend-verified payment authorization BEFORE confirmation.

### 2. WorkOrderStatus
**Transitions**: ASSIGNED → ACCEPTED | REJECTED → ON_THE_WAY → ARRIVED → STARTED → COMPLETED | CANCELLED
- Governs the overall job lifecycle from the dispatch perspective.

### 3. ServiceVisitStatus
*(Note: Separate from WorkOrderStatus to support 1:N cardinality)*
**Transitions**: SCHEDULED → ON_THE_WAY → ARRIVED → STARTED → COMPLETED | CANCELLED | FAILED
- Each `ServiceVisit` has its own status.
- One `WorkOrder` may have MULTIPLE `ServiceVisits` (1:N). Supports failed visits, rescheduled visits, follow-ups.
- **FAILED/CANCELLED Visit**: Creates a new `ServiceVisit` on the same `WorkOrder` for rescheduling.
- **COMPLETED Visit**: Triggers `visit.completed` event → inventory deduction → invoice generation.

### 4. PaymentStatus
**Transitions**: PENDING → AUTHORIZED → PAID | PARTIAL | FAILED.
- **Secondary**: PAID → REFUNDED | PARTIALLY_REFUNDED
- Status strictly managed by the backend webhook processor, never overridable by client requests.

## 3. Business Invariants

1. **Transactional Slot Locking**: A booking can only be `CONFIRMED` if an available slot exists and is locked transactionally.
2. **Coupon Limits**: A coupon can only be used once per customer (enforced via `UNIQUE(coupon_id, customer_id)` in `coupon_redemptions` when perUserLimit=1).
3. **Technician Concurrency**: A technician cannot accept a job if they have an active `STARTED` job.
4. **Authoritative Payments**: Payment state transitions are BACKEND ONLY.
5. **Inventory Integrity**: Inventory deduction is transactional. `CHECK (current_quantity >= 0)`.
6. **Immutable Invoices**: Invoice numbers are generated once and are strictly immutable after issuance.
7. **Audit Append-Only**: Rows in `audit_logs` are NEVER updated or deleted.

## 4. Cardinality Summary Table

| Relationship | Cardinality | Foreign Key | Delete Rule |
| :--- | :--- | :--- | :--- |
| customers → bookings | 1:N | `customer_id` | RESTRICT |
| bookings → booking_items | 1:N | `booking_id` | CASCADE |
| bookings → work_orders | 1:N | `booking_id` | RESTRICT |
| work_orders → service_visits | 1:N | `work_order_id` | RESTRICT |
| service_visits → service_material_usage | 1:N | `visit_id` | RESTRICT |
| chemical_batches → service_material_usage | 1:N | `batch_id` | RESTRICT |
| payments → payment_events | 1:N | `payment_id` | RESTRICT |
| bookings → payments | 1:N | `booking_id` | RESTRICT |
| coupons → coupon_redemptions | 1:N | `coupon_id` | RESTRICT |
| customers → coupon_redemptions | 1:N | `customer_id` | RESTRICT |
| amc_contracts → amc_schedules | 1:N | `contract_id` | RESTRICT |
