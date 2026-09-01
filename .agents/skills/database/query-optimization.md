---
name: query-optimization
description: Optimizing PostgreSQL queries for Pest Control ERP
category: database
triggers:
  - Optimize database query
  - Fix slow query
  - Add database index
inputs:
  - Slow SQL query
  - Execution plan
outputs:
  - Optimized SQL
  - Index definitions
dependencies:
  - postgresql-schema
related_skills:
  - relational-modeling
---

# Skill: Query Optimization

## Purpose
To ensure all database interactions in the Pest Control ERP perform efficiently under load, minimizing latency and resource consumption using PostgreSQL 16 features.

## When to Use / When NOT to Use
**Use When:** Designing complex read operations, generating reports, or debugging performance bottlenecks.
**NOT to Use:** Prematurely on small tables (< 1000 rows) where sequential scans are faster, or for trivial primary key lookups.

## Required Context
Familiarity with PostgreSQL's EXPLAIN ANALYZE output and Spring Data JPA/Hibernate's query generation behavior.

## Domain Rules & Constraints
1. **EXPLAIN ANALYZE:** Always validate complex queries using `EXPLAIN ANALYZE` before considering them optimized. Look for sequential scans on large tables and high-cost nodes.
2. **Indexing Strategy:**
   * Use **Composite Indexes** for queries that filter on multiple columns simultaneously (e.g., `WHERE agency_id = ? AND status = ?`). Order columns by selectivity (most selective first).
   * Consider **Covering Indexes** (`INCLUDE` clause) for frequently accessed data to allow Index-Only Scans.
   * Do not over-index. Indexes speed up reads but slow down writes (INSERT/UPDATE/DELETE).
3. **N+1 Query Prevention:** When using JPA/Hibernate, use `JOIN FETCH` or `@EntityGraph` to fetch related entities in a single query rather than lazily loading them in a loop.
4. **Pagination:**
   * Use **Keyset Pagination** (cursor-based) for endless scrolling or large datasets (e.g., `WHERE id > last_seen_id ORDER BY id LIMIT 20`).
   * Avoid deep **Offset Pagination** (`OFFSET 500000`) as it requires scanning and discarding rows.
5. **Materialized Views:** Use for heavy analytical queries or reports that don't need real-time data but require fast read access.

## Business Rules
*   Ensure customer-facing APIs respond in under 200ms. Dispatch and scheduling screens must load quickly even with hundreds of technicians.
*   Reporting queries can be slower but should not block operational transactions.

## Database Considerations
*   PostgreSQL 16 improves query execution for parallelism. Leverage this for heavy analytical tasks if necessary.
*   Regularly analyze tables (`ANALYZE table_name`) to keep statistics updated for the query planner.

## Validation Checklist
- [ ] Has `EXPLAIN ANALYZE` been run to verify the query plan?
- [ ] Are composite indexes ordered correctly based on selectivity?
- [ ] Is N+1 loading prevented in the ORM?
- [ ] Is pagination efficient (keyset preferred for deep pagination)?
- [ ] Are covering indexes utilized for critical read-heavy paths?

## Common Mistakes
*   Adding individual indexes on every column instead of composite indexes.
*   Using `OFFSET` for pagination on very large datasets.
*   Ignoring ORM-generated SQL, leading to N+1 problems.
*   Failing to consider the overhead of maintaining indexes on write-heavy tables like `audit_logs`.

## Related Skills
- `postgresql-schema`
- `relational-modeling`
