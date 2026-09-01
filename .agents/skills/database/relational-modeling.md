---
name: relational-modeling
description: Relational data modeling for the Pest Control ERP
category: database
triggers:
  - Design new domain
  - Map entity relationships
  - Plan database schema
inputs:
  - Business domain requirements
outputs:
  - Entity relationship map
dependencies:
  - postgresql-schema
related_skills:
  - domain/*
---

# Skill: Relational Modeling

## Purpose
To define and enforce the overall entity relationship structure for the Pest Control ERP, encompassing over 28 entities, ensuring strict adherence to the Domain Model rules and decoupling where necessary.

## When to Use / When NOT to Use
**Use When:** Designing a new feature, adding entities, or refactoring how data domains relate to each other.
**NOT to Use:** For NoSQL design or transient application state modeling.

## Required Context
The core rule of the ERP's operational flow must be maintained:
**Booking (Commercial intent) → Work Order (Dispatch grouping) → Service Visit (Physical execution).**
These three are distinctly separated and must not be collapsed into a single table.

## Domain Rules & Constraints
1.  **Strict Separation of Concerns:**
    *   **Booking:** Represents the customer's request, financial agreement, and expected services.
    *   **Work Order:** Represents the dispatch unit. A booking might result in multiple work orders over time (e.g., an AMC booking yields 4 quarterly work orders).
    *   **Service Visit:** Represents a single trip by a technician. A work order might require multiple visits if it's not completed on the first attempt.
2.  **Entity Mapping:**
    *   `customers` (1) - (N) `customer_addresses`
    *   `customers` (1) - (N) `bookings`
    *   `bookings` (1) - (N) `work_orders`
    *   `work_orders` (1) - (N) `service_visits`
    *   `agencies` (1) - (N) `employees`
    *   `work_orders` (N) - (1) `employees` (assigned_technician)
    *   `bookings` (1) - (N) `payments`
    *   `bookings` (1) - (N) `invoices`
3.  **Auditing:** Critical entities (bookings, work orders, payments) must have their changes tracked in `audit_logs`.

## Business Rules
*   Do not allow a `Service Visit` to exist without a parent `Work Order`.
*   Do not allow a `Work Order` to exist without a parent `Booking` or `AMC Contract`.
*   Financials (Payments, Invoices) tie back to the `Booking`, not the individual visits, except in cases of specific visit-level upselling, which should be modeled as an add-on to the Booking or a new Booking entirely.

## Database Considerations
*   Ensure all FK relationships accurately reflect these constraints (e.g., `work_orders.booking_id` is NOT NULL).
*   Avoid circular dependencies between tables. Use intermediate joining tables for Many-to-Many (e.g., `employee_skills`).

## Validation Checklist
- [ ] Is the Booking -> Work Order -> Service Visit hierarchy preserved?
- [ ] Are Many-to-Many relationships properly modeled with join tables?
- [ ] Are Foreign Keys mandatory (`NOT NULL`) where appropriate?
- [ ] Has denormalization been avoided unless strictly necessary for performance (and justified)?

## Common Mistakes
*   Collapsing `Booking` and `Work Order` into one table, which breaks the AMC (Annual Maintenance Contract) logic.
*   Storing financial totals only on the `Invoice` and not tracking the agreed amount on the `Booking`.
*   Failing to handle multiple addresses for a single customer.

## Related Skills
- `postgresql-schema`
- `domain/booking`
- `domain/work-order`
- `domain/service-visit`
