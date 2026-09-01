---
name: customer-payment-flow
description: Skill for Customer Android payment flow.
category: android
triggers:
  - implement payments
inputs:
  - payment endpoints
outputs:
  - payment gateway integration
dependencies: []
related_skills:
  - customer-booking-flow
---

# customer-payment-flow

## Purpose
Skill for Customer Android payment flow. Cover: initiate payment via Spring Boot, open Razorpay/Stripe SDK, never trust SDK success callback alone — always poll /api/v1/payments/{id} for server-confirmed status.

## When to Use
Integrating payment gateways in the customer app.

## When NOT to Use
For admin invoice generation.

## Required Context
- Backend payment initiation endpoint

## Inputs
- Booking ID

## Expected Outputs
- Payment success/failure handling

## Rules & Constraints
1. Never trust the client SDK success callback alone.
2. Always poll the backend for final authoritative status.

## Step-by-Step Workflow
1. Call backend to initiate payment.
2. Launch SDK with payment token/ID.
3. On SDK success, poll backend endpoint.
4. Update UI based on server confirmation.

## Validation Checklist
- [ ] Payment initiation goes through backend.
- [ ] Server validates payment before UI says success.

## Common Mistakes
- Trusting client SDK success callback directly.

## Example Usage
```java
// Poll server
```

## Related Skills
- customer-booking-flow

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
