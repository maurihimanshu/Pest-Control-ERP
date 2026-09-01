---
name: entity-design
description: Designs JPA entities with relationships, fetch strategies, and PostgreSQL optimizations.
category: backend
triggers:
  - create entity
  - define schema
inputs:
  - domain model
outputs:
  - JPA Entity classes
dependencies:
  - architecture-rules
related_skills:
  - repository-layer
---

# Skill: Entity Design

## Purpose
To map domain objects to PostgreSQL relational tables using Hibernate/JPA.

## Rules & Constraints
1. Annotate with `@Entity` and `@Table(name = "plural_name")`.
2. Use `@Id` with generated values (UUID or Sequence, avoid Identity if bulk inserts are needed).
3. Use `@Version` for optimistic locking on highly concurrent entities (e.g., Inventory, WorkOrder).
4. **Fetch Strategy**: `FetchType.LAZY` MUST be used for all `@OneToMany` and `@ManyToOne` associations.
5. Avoid bidirectional relationships if possible; if needed, carefully manage `mappedBy` and `cascade`.
6. Include Auditing fields (`createdAt`, `updatedAt`, `createdBy`).

## Step-by-Step Workflow
1. Define the class in the `domain` package.
2. Add fields and map to columns.
3. Define relationships with other entities within the SAME module.
4. Add auditing annotations (`@CreatedDate`, `@LastModifiedDate`).
5. Generate `equals()` and `hashCode()` using the business key or ID (be careful with un-persisted entities).

## Validation Checklist
- [ ] No `FetchType.EAGER`.
- [ ] Optimistic locking used where applicable.
- [ ] Lombok `@Data` avoided on Entities (use `@Getter`, `@Setter`, and custom `equals`/`hashCode` to prevent stack overflows on relationships).

## Common Mistakes
- Using `@Data` causing infinite loops in `toString()` via relationships.
- Referencing entities from other modules directly, violating module boundaries.
