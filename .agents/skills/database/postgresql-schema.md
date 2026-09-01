---
name: postgresql-schema
description: Designing PostgreSQL 16 table schemas for Pest Control ERP
category: database
triggers:
  - Create new database table
  - Design database schema
  - Write DDL for new entity
inputs:
  - Entity definition
  - Expected access patterns
outputs:
  - PostgreSQL DDL script
dependencies:
  - relational-modeling
related_skills:
  - flyway-migration
---

# Skill: PostgreSQL Schema Design

## Purpose
To define the standard for creating PostgreSQL 16 tables within the Pest Control ERP, ensuring high performance, consistency, data integrity, and strict adherence to naming conventions and data types.

## When to Use / When NOT to Use
**Use When:** Designing a new table or altering an existing one in the ERP system.
**NOT to Use:** For NoSQL document stores or temporary caches like Redis. Do not use for legacy database updates if they completely violate these standards.

## Required Context
You must know the entity relationships, fields, data types, and primary key requirements. The database is PostgreSQL 16, which brings specific optimizations and features.

## Domain Rules & Constraints
1. **Naming Conventions:** All tables, columns, constraints, and indexes MUST use `snake_case`. Table names should be plural (e.g., `bookings`, `customers`).
2. **Primary Keys:** Must be UUIDs using `gen_random_uuid()` as the default.
3. **Timestamps:** Every table (except pure join tables, though often recommended there too) MUST have `created_at` (default `now()`) and `updated_at` (default `now()`).
4. **Data Integrity:** Maximize the use of `NOT NULL`.
5. **Constraints:** Use `CHECK` constraints for data validation (e.g., ensuring `price >= 0` or status strings fall within valid enums).
6. **Foreign Keys:** Explicitly define all foreign keys with appropriate `ON DELETE` actions (usually `RESTRICT` to prevent accidental cascading deletions).

## Entity Structure
*   `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
*   Business fields with `NOT NULL` where applicable
*   `created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL`
*   `updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL`

## Business Rules
*   Do not use auto-incrementing integers (`SERIAL` or `BIGSERIAL`) for primary keys unless specifically required for legacy integration or strict sequential ordering outside of invoices. Use UUIDs.
*   Enforce referential integrity at the database level. Do not rely solely on the application layer.
*   Use `JSONB` for unstructured or loosely structured data like `metadata`, `checklists`, or `audit_logs`.

## Database Considerations
*   Use `TIMESTAMP WITH TIME ZONE` (or `timestamptz`) instead of plain `TIMESTAMP`.
*   Index foreign key columns, as they are frequently used in `JOIN` conditions.
*   Name constraints explicitly to make error messages readable: `CONSTRAINT fk_table_ref_table FOREIGN KEY...`

## Validation Checklist
- [ ] Table name is plural snake_case.
- [ ] Columns are snake_case.
- [ ] Primary key is UUID with `gen_random_uuid()`.
- [ ] `created_at` and `updated_at` exist and are `TIMESTAMP WITH TIME ZONE`.
- [ ] Appropriate columns have `NOT NULL` constraints.
- [ ] Foreign keys are defined with explicit names and `ON DELETE RESTRICT`.
- [ ] `CHECK` constraints are used for finite state lists or numeric boundaries.

## Common Mistakes
*   Using `camelCase` for column names.
*   Forgetting to index foreign keys.
*   Relying on application code for data validation that could be a `CHECK` constraint.
*   Using `VARCHAR(255)` out of habit instead of unbounded `TEXT` (PostgreSQL handles `TEXT` efficiently).

## Example Usage
```sql
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'CONFIRMED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_bookings_customer_id FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);
CREATE INDEX idx_bookings_customer_id ON bookings(customer_id);
```

## Related Skills
- `flyway-migration`
- `relational-modeling`
