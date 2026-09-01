---
name: audit-tables
description: Designing append-only audit_logs table in PostgreSQL
category: database
triggers:
  - Add audit logging
  - Track entity changes
  - Design audit table
inputs:
  - Entities to audit
outputs:
  - Audit table schema
dependencies:
  - postgresql-schema
related_skills:
  - domain/booking
---

# Skill: Audit Tables

## Purpose
To maintain a strict, append-only ledger of changes to critical business entities within the Pest Control ERP, ensuring compliance, traceability, and debugging capabilities.

## When to Use / When NOT to Use
**Use When:** Tracking changes to entities like Bookings, Work Orders, Payments, Users, or Inventory.
**NOT to Use:** For high-volume transient data like GPS location pings (use a dedicated time-series or separate table), or for unstructured application logs.

## Required Context
The `audit_logs` table is the system of record for "who changed what and when." It must be immutable.

## Domain Rules & Constraints
1. **Append-Only:** The `audit_logs` table must never be updated or deleted. Database permissions should reflect this for application users.
2. **Schema Structure:**
   * `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
   * `entity_type VARCHAR(255) NOT NULL` (e.g., 'BOOKING', 'WORK_ORDER')
   * `entity_id UUID NOT NULL`
   * `action VARCHAR(50) NOT NULL` (e.g., 'CREATE', 'UPDATE', 'DELETE')
   * `actor_id UUID` (The user who performed the action, nullable for system actions)
   * `old_value JSONB` (State before the change)
   * `new_value JSONB` (State after the change)
   * `ip_address VARCHAR(45)`
   * `created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL`
3. **Immutability:** Do not include an `updated_at` column.

## Business Rules
*   Every state change in a Booking or Work Order must generate an audit log entry.
*   Sensitive data (like plain text passwords or full credit card numbers, which shouldn't be stored anyway) must be masked before being serialized into the JSONB payloads.

## Database Considerations
*   Since `old_value` and `new_value` are JSONB, they can be queried using PostgreSQL JSON operators (e.g., to find all logs where status changed to 'CANCELLED').
*   Partitioning: If the table grows rapidly, consider partitioning by date (`created_at`).
*   Indexing: Index `entity_type` and `entity_id` together for fast retrieval of an entity's history. Index `actor_id` for tracing user actions.

## Validation Checklist
- [ ] Is the table append-only (no updates/deletes permitted)?
- [ ] Are JSONB columns used for flexible snapshot storage?
- [ ] Are the required indexing strategies in place (`entity_id` + `entity_type`)?
- [ ] Does the application capture the `actor_id` correctly from the security context?

## Common Mistakes
*   Attempting to update an audit log record.
*   Storing massive amounts of unchanged data; ideally, only store the delta, or store the full snapshot if storage isn't an issue, but be consistent. Our standard is full snapshot in JSONB for simplicity of reconstruction.
*   Forgetting to index the `entity_id`.

## Related Skills
- `postgresql-schema`
- `security/spring-security-config`
