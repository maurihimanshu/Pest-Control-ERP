---
name: api-request-response-contracts
description: Skill for request/response contract design.
category: api
triggers:
  - design contracts
inputs:
  - DTOs
outputs:
  - generic response wrappers
dependencies: []
related_skills:
  - api-rest-design
---

# api-request-response-contracts

## Purpose
Skill for request/response contract design. Cover: standard `ApiResponse<T>` wrapper `{data, message, timestamp, traceId}`, `ApiErrorResponse` `{code, message, timestamp, traceId, validationErrors[]}`, pagination response `{content, page, size, totalElements, totalPages}`, and explicit exemptions for non-JSON or native endpoints.

## When to Use
Standardizing API outputs across all Spring MVC `@RestController` endpoints.

## When NOT to Use
For internal service method signatures.

## Required Context
- Spring Web, Jackson, Springdoc

## Inputs
- Raw data payloads and DTOs

## Expected Outputs
- Standardized REST envelopes with clear exemption rules

## Rules & Constraints
1. **Standard JSON Resources:** Wrapped in `ApiResponse<T>`.
2. **Standard Errors:** Return `ApiErrorResponse` with HTTP status, machine error code, message, timestamp, trace ID, and optional `validationErrors[]`.
3. **Explicit Wrapper Exemptions:**
   - **File / Media Downloads:** Return native `ResponseEntity<Resource>` or `StreamingResponseBody` with raw binary stream and appropriate `Content-Type` / `Content-Disposition` headers (NO JSON envelope).
   - **HTTP 204 No Content:** Return empty response body (`ResponseEntity.noContent().build()`).
   - **Payment Webhook Endpoints:** Return gateway-specific response (e.g. `HTTP 200 OK` with raw `{"status": "ok"}` or empty body as required by Razorpay/Stripe).
4. Always include `X-Correlation-ID` / `traceId` from MDC.

## Step-by-Step Workflow
1. Create `ApiResponse<T>` record.
2. Create `ApiErrorResponse` record with `ValidationError` list.
3. Update standard controllers to return `ApiResponse<T>`.
4. Leave file streaming and webhook controllers unwrapped.
5. Update `GlobalExceptionHandler` with `@RestControllerAdvice`.

## Validation Checklist
- [ ] Standard JSON APIs return `ApiResponse<T>`.
- [ ] File downloads stream native binary without JSON wrapper.
- [ ] Webhooks return gateway-expected format.
- [ ] Trace IDs are present in all JSON responses and error envelopes.

## Common Mistakes
- Wrapping binary file downloads or PDF streams in an `ApiResponse<T>`, breaking client PDF viewers.
- Returning raw uncaught exception stack traces to clients.


## Example Usage
```java
public record ApiResponse<T>(T data, String message, String traceId) {}
```

## Related Skills
- api-rest-design

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
