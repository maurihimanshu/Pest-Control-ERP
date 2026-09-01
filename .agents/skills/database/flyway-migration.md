---
name: flyway-migration
description: Creating and managing Flyway migration scripts
category: database
triggers:
  - Create database migration
  - Add column to table
  - Write Flyway script
inputs:
  - Database schema changes
  - Migration sequence number
outputs:
  - Flyway .sql file
dependencies:
  - postgresql-schema
related_skills:
  - relational-modeling
---

# Skill: Flyway Migration

## Purpose
To manage database schema evolution and data migrations using Flyway, ensuring that database changes are versioned, repeatable, and safely applied across all environments in the Pest Control ERP.

## When to Use / When NOT to Use
**Use When:** Adding, modifying, or removing tables, columns, indexes, or static reference data in the database.
**NOT to Use:** For one-off scripts on production data, manual fixes, or application-level migrations that require complex business logic best suited for a Java script.

## Required Context
Flyway migrations execute sequentially based on their filename. You must ensure you are using the next available version number and that your SQL syntax is valid for PostgreSQL 16.

## Domain Rules & Constraints
1. **Naming Convention:** Files MUST follow the pattern `V{n}__{description}.sql`. Notice the double underscore. (e.g., `V1__init.sql`, `V2__add_booking_notes.sql`).
2. **Safe ALTER TABLE:** Do not lock large tables in production for extended periods. When adding columns with defaults, rely on PostgreSQL 11+ fast defaults.
3. **No Column Drops (Short Term):** NEVER drop a column or table in a single migration cycle if the application is still using it. Use a deprecation pattern: add new column, sync data, deploy app to use new column, drop old column in a later release.
4. **Data Migrations:** Separate complex data migrations from schema migrations if they are large or risky, possibly using Spring Batch or a separate Java-based migration tool if logic is too complex for SQL.
5. **Rollback:** While Flyway community edition does not support automatic down migrations easily, you should design migrations to be backward compatible (expand and contract pattern) to allow application rollbacks.

## Business Rules
*   Every schema change must be documented as a Flyway script.
*   Scripts are immutable once deployed to any shared environment (dev/staging/prod). Never modify an existing script after it has been executed.

## Database Considerations
*   Be cautious with `CREATE INDEX` on large tables. Use `CREATE INDEX CONCURRENTLY` for existing large tables, but note that Flyway runs migrations in a transaction by default, and concurrent index creation cannot run in a transaction. You might need to configure Flyway for non-transactional migrations for those specific files.
*   Always test migrations against a recent production clone or staging environment.

## Validation Checklist
- [ ] Filename follows `V{version}__{description}.sql` exactly (double underscore).
- [ ] Next sequential version number is used.
- [ ] No existing columns or tables are dropped if they are in use.
- [ ] Default values are handled safely.
- [ ] Foreign keys have appropriate indices.
- [ ] SQL syntax is valid PostgreSQL 16.

## Common Mistakes
*   Using a single underscore instead of a double underscore in the filename.
*   Modifying a previously executed script (causes checksum errors in Flyway).
*   Dropping a column that the currently running version of the application still expects.
*   Writing syntax specific to MySQL or Oracle instead of PostgreSQL.

## Example Usage
```sql
-- File: V5__add_cancellation_reason_to_bookings.sql
ALTER TABLE bookings
ADD COLUMN cancellation_reason TEXT;

-- Safe to add an index if table isn't huge, otherwise consider CONCURRENTLY (which needs special handling)
CREATE INDEX idx_bookings_status ON bookings(status);
```

## Related Skills
- `postgresql-schema`
