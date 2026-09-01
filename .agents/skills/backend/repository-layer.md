---
name: repository-layer
description: Designs Spring Data JPA repositories with query methods and projections.
category: backend
triggers:
  - create repository
  - add database access
inputs:
  - entity context
outputs:
  - JpaRepository interface
dependencies:
  - entity-design
related_skills:
  - service-layer
---

# Skill: Repository Layer Design

## Purpose
To handle data persistence and retrieval from PostgreSQL using Spring Data JPA.

## Rules & Constraints
1. Repositories must be interfaces extending `JpaRepository<Entity, ID>`.
2. Place in the module's `repository` package.
3. Use derived query methods where possible (`findByStatusAndDate...`).
4. Use `@Query` for complex JPQL or native queries.
5. Use Projections (interfaces) for read-heavy operations where the full entity is not needed, improving performance.
6. Repositories must be package-private or restricted if you want to strictly enforce access via the module's Service layer, though public is standard in many Spring apps. Ensure modules do NOT cross-inject them.

## Step-by-Step Workflow
1. Create the interface extending `JpaRepository`.
2. Add necessary finder methods.
3. Validate JPQL syntax if using `@Query`.
4. Ensure pagination is used for collections (`Pageable` parameter).

## Validation Checklist
- [ ] `Pageable` used for unbounded lists.
- [ ] `@Query` uses JPQL securely (no SQL injection risks).

## Common Mistakes
- Returning huge lists without pagination.
- Using N+1 queries by forgetting `JOIN FETCH` in `@Query` when loading associations.
