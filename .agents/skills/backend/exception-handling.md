---
name: exception-handling
description: Configures global exception handling for REST APIs.
category: backend
triggers:
  - handle exceptions
  - standardize errors
inputs:
  - expected exception types
outputs:
  - ControllerAdvice class
dependencies:
  - rest-controller
related_skills:
  - architecture-rules
---

# Skill: Exception Handling

## Purpose
To provide consistent, structured error responses to API clients, ensuring no stack traces leak.

## Rules & Constraints
1. Use `@RestControllerAdvice`.
2. Define a standard `ErrorResponse` DTO: `{ code, message, timestamp, traceId, details }`.
3. Map standard exceptions:
   - `EntityNotFoundException` -> 404 Not Found
   - `IllegalArgumentException` / `MethodArgumentNotValidException` -> 400 Bad Request
   - `AccessDeniedException` -> 403 Forbidden
   - Custom Domain Exceptions (e.g., `InvalidBookingStateException`) -> 409 Conflict or 400 Bad Request.
   - `Exception` -> 500 Internal Server Error.

## Step-by-Step Workflow
1. Create a `GlobalExceptionHandler` annotated with `@RestControllerAdvice`.
2. Add `@ExceptionHandler` methods for each category of exception.
3. Construct the `ErrorResponse` payload.
4. Log the error (at `ERROR` level for 500s, `WARN` or `INFO` for 4xxs), including a correlation ID.

## Validation Checklist
- [ ] No stack traces in API response.
- [ ] Appropriate HTTP status codes used.
- [ ] Validation errors include field-level details.

## Common Mistakes
- Returning 200 OK with a custom error code instead of using standard HTTP status codes.
- Failing to log exceptions that return 500.
