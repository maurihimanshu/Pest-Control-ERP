---
name: module-boundary-validation
description: Validates that Spring Boot modular monolith boundaries are respected.
category: architecture
triggers:
  - check boundaries
  - validate modules
inputs:
  - module name
outputs:
  - boundary violation report
dependencies:
  - architecture-rules
related_skills:
  - architecture-discovery
---

# Skill: Module Boundary Validation

## Purpose
To ensure that modules remain decoupled and only communicate via designated public interfaces or async events, preventing a "Big Ball of Mud".

## Rules & Constraints
1. Modules must only communicate via `@Service` interfaces or RabbitMQ events.
2. **NEVER** inject a `Repository` from Module A into a `Service` in Module B.
3. **NEVER** directly access the database tables of another module bypassing its service layer.
4. DTOs should be used for cross-module data transfer, not internal JPA `@Entity` classes (to avoid lazy-loading issues and deep coupling).

## Step-by-Step Workflow
1. Identify the module being validated (e.g., `com.pestcontrol.modules.bookings`).
2. Grep the module's source directory for imports from other modules (`import com.pestcontrol.modules.othermodule.*`).
3. For each import, verify it is a Service interface, a DTO, or an Event class.
4. Flag any imports of `Repository`, `Entity`, or internal implementation classes as violations.
5. Provide refactoring suggestions (e.g., expose a new method in the target module's Service, or publish an Event).

## Validation Checklist
- [ ] No cross-module Repository injections.
- [ ] No cross-module Entity usages.
- [ ] No direct SQL joins across separate module schemas (if strict logical separation is enforced).

## Common Mistakes
- Exposing entities in module APIs for convenience, leading to `LazyInitializationException` in other modules.
