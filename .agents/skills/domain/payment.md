---
name: payment
description: Managing the Payment domain and external gateway integrations.
category: domain
triggers:
  - Process customer payment
  - Handle webhook from Stripe/Razorpay
inputs:
  - Payment gateway responses
outputs:
  - Payment service implementation
dependencies:
  - domain/booking
related_skills:
  - domain/invoice
---

# Skill: Payment Domain

## Purpose
To securely and reliably track financial transactions, interface with payment gateways, handle Cash on Delivery (COD), and manage payment states independent of client applications.

## When to Use / When NOT to Use
**Use When:** Processing credit cards, handling UPI/wallet webhooks, or logging cash collected by technicians.
**NOT to Use:** For generating the official tax invoice document (use Invoice domain).

## Required Context
Never trust the client application for payment state. The backend must be the source of truth, relying on secure webhooks or server-to-server API calls to gateways.

## Domain Rules & Constraints
1. **Idempotency:** Webhook processing MUST be idempotent. Gateways often send the same event multiple times.
2. **Security:** Verify all webhook HMAC signatures before processing.
3. **State Machine:**
   `PENDING` -> `AUTHORIZED` -> `PAID`
   `PENDING` -> `FAILED`
   `PAID` -> `REFUNDED` / `PARTIALLY_REFUNDED`
4. **COD Handling:** Cash collected must be marked `PAID` by authorized personnel (tech or admin) and reconciled later.

## Entity Structure
*   `id` UUID
*   `booking_id` UUID
*   `amount` DECIMAL
*   `currency` VARCHAR (default 'INR' or 'USD')
*   `method` VARCHAR (CARD, UPI, CASH)
*   `gateway` VARCHAR (STRIPE, RAZORPAY, MANUAL)
*   `gateway_transaction_id` VARCHAR
*   `status` VARCHAR
*   `webhook_payload` JSONB (for debugging)
*   `created_at`, `updated_at`

## Spring Service Methods
*   `Payment createPaymentIntent(UUID bookingId, BigDecimal amount)`
*   `void handleWebhook(String payload, String signature)`
*   `Payment recordCashCollection(UUID bookingId, BigDecimal amount, UUID employeeId)`

## Database Considerations
*   Unique constraint on `gateway_transaction_id` to prevent double counting.
*   Ensure high precision `DECIMAL(10,2)` for amounts.

## RabbitMQ Events
*   `PaymentCompletedEvent` -> Highly critical. Consumed by Booking service to update status, and by Invoice service to generate the PDF.

## Validation Checklist
- [ ] Are webhooks verified via HMAC?
- [ ] Is webhook processing idempotent?
- [ ] Is double-charging prevented via unique transaction IDs?
- [ ] Are events published only AFTER the DB transaction commits (Outbox pattern recommended)?

## Common Mistakes
*   Trusting a mobile app's "payment success" API call without verifying with the gateway.
*   Not handling partial payments correctly.
*   Failing to implement idempotency, resulting in multiple `PaymentCompletedEvent` triggers.

## Related Skills
- `domain/invoice`
- `domain/booking`
