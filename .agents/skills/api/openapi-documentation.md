---
name: api-openapi-documentation
description: Skill for OpenAPI documentation.
category: api
triggers:
  - document api
inputs:
  - controllers
outputs:
  - swagger docs
dependencies: []
related_skills:
  - api-rest-design
---

# api-openapi-documentation

## Purpose
Skill for OpenAPI/Swagger documentation with Springdoc. Cover: @Operation, @ApiResponse, @Schema annotations, grouping by module, generating /api-docs endpoint.

## When to Use
Documenting new endpoints for frontend developers.

## When NOT to Use
Internal private methods.

## Required Context
- Springdoc OpenAPI

## Inputs
- Controller and DTOs

## Expected Outputs
- Auto-generated Swagger UI

## Rules & Constraints
1. Every endpoint must have `@Operation`.
2. DTOs must have `@Schema` with examples.
3. Document all possible error responses.

## Step-by-Step Workflow
1. Add Springdoc dependency.
2. Annotate controllers.
3. Annotate fields with descriptions and examples.
4. Verify `/swagger-ui.html`.

## Validation Checklist
- [ ] Auth requirements are documented.
- [ ] Request bodies have examples.

## Common Mistakes
- Leaving endpoints undocumented, forcing frontends to guess.

## Example Usage
```java
@Operation(summary = "Create booking")
// endpoint
```

## Related Skills
- api-rest-design

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
