---
name: rest-controller
description: Designs Spring MVC REST controllers with proper mappings, validation, and DTOs.
category: backend
triggers:
  - create controller
  - add api endpoint
inputs:
  - domain context
  - endpoint requirements
outputs:
  - RestController class
dependencies:
  - dto-design
  - exception-handling
related_skills:
  - service-layer
---

# Skill: REST Controller Design

## Purpose
To expose backend services via standardized RESTful HTTP APIs.

## Rules & Constraints
1. Always use `@RestController` and `@RequestMapping("/api/v1/{resource}")`.
2. **Never** accept or return JPA `@Entity` classes directly. Always use DTOs.
3. Use `@Valid` for input validation.
4. Use standard HTTP methods: GET (read), POST (create), PUT/PATCH (update), DELETE (remove).
5. Controllers must remain thin, delegating business logic to the `@Service` layer.
6. Enforce security using `@PreAuthorize` where applicable.

## Step-by-Step Workflow
1. Create the Controller class in the `web` package.
2. Inject the necessary Service interface via constructor injection (use `final` fields).
3. Define endpoint methods mapping HTTP requests to Service calls.
4. Map Service layer results to Response DTOs.
5. Handle Location headers for POST (201 Created) responses.

## Validation Checklist
- [ ] Constructor injection used.
- [ ] No business logic in controller.
- [ ] Only DTOs in method signatures.
- [ ] Proper HTTP status codes used (200, 201, 204).

## Common Mistakes
- Returning 200 OK for entity creation instead of 201 Created.
- Leaking database exceptions directly to the client instead of mapping them via `@RestControllerAdvice`.
