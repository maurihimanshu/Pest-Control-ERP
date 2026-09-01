---
name: dto-design
description: Designs request and response DTOs using Java Records and Bean Validation.
category: backend
triggers:
  - create dto
  - define api contract
inputs:
  - API requirements
outputs:
  - DTO classes/records
dependencies:
  - rest-controller
related_skills:
  - validation
---

# Skill: DTO Design

## Purpose
To strictly decouple the internal domain model (Entities) from the external API contracts (JSON).

## Rules & Constraints
1. Use **Java 21 Records** for DTOs to ensure immutability.
2. Group related DTOs if small, or keep in a dedicated `dto` package.
3. Apply standard Bean Validation annotations (`@NotNull`, `@NotBlank`, `@Size`, `@Min`, `@Max`).
4. Provide mapping logic (via MapStruct or static factory methods) in the Service or a dedicated Mapper class.
5. **Never** return password hashes or internal database IDs if UUIDs or business keys are preferred for external access.

## Step-by-Step Workflow
1. Identify the data required for a specific request or response.
2. Create a Record: `public record BookingRequestDto(@NotBlank String customerId, @NotNull LocalDate serviceDate) {}`.
3. Add validation annotations.
4. Implement conversion logic mapping to/from the Entity.

## Validation Checklist
- [ ] Record syntax used.
- [ ] Validation annotations present.
- [ ] No internal state leaked.

## Common Mistakes
- Using mutable classes with getters/setters instead of Records.
- Over-fetching database fields into the DTO that the client doesn't need.
