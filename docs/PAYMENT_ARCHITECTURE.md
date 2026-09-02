# Payment & Invoicing Architecture Specification
## Gateway Integration, Webhook Deduplication & Automated Invoicing

**Document Version:** 2.0.0  
**Payment Gateways:** Razorpay / Stripe (Multi-Gateway Ready)  
**PDF Engine:** OpenPDF inside Spring Boot  
**Transactional Store:** PostgreSQL 16  
**Reference:** [`docs/CONCURRENCY_AND_IDEMPOTENCY.md`](CONCURRENCY_AND_IDEMPOTENCY.md)  
**Date:** September 2026  

---

## 1. Zero-Trust Payment Architecture

The payment architecture adheres to a strict **Zero-Trust Client** model: mobile and web clients are never trusted to declare that a payment has succeeded. All payment confirmations are verified via cryptographically signed webhooks or direct server-to-server gateway queries.

```text
 ┌────────────────┐              ┌────────────────────────┐              ┌──────────────────┐
 │  Customer App  │              │ Spring Boot Backend API│              │ Payment Gateway  │
 └───────┬────────┘              └───────────┬────────────┘              └────────┬─────────┘
         │                                   │                                    │
         │ 1. POST /api/v1/payments/initiate │                                    │
         ├──────────────────────────────────►│ 2. Create Payment (PENDING)        │
         │                                   │ 3. Init Gateway Order              │
         │                                   ├───────────────────────────────────►│
         │                                   │◄───────────────────────────────────┤
         │ 4. Return Gateway Order ID        │    (Order ID: order_893247)        │
         │◄──────────────────────────────────┤                                    │
         │                                   │                                    │
         │ 5. Complete Native SDK Checkout   │                                    │
         ├───────────────────────────────────┼───────────────────────────────────►│
         │                                   │                                    │
         │                                   │ 6. Async Webhook (HMAC Signed)     │
         │                                   │◄───────────────────────────────────┤
         │                                   │ 7. Verify Webhook Signature        │
         │                                   │ 8. Atomic payment_events Insert    │
         │                                   │ 9. Transactional Payment Update    │
         │                                   │ 10. Write OutboxEvent              │
         │                                   │                                    │
         │ 11. Poll /api/v1/payments/{id}    │                                    │
         │◄──────────────────────────────────┤                                    │
```

---

## 2. Webhook Signature Verification & Idempotency

### 2.1 HMAC-SHA256 Signature Verification
Incoming webhooks to `/api/v1/payments/webhooks/{gateway}` are cryptographically validated before any payload processing:
* **Razorpay:** Verifies `X-Razorpay-Signature` against the raw HTTP request body using `HmacSHA256` with the configured webhook secret.
* **Stripe:** Verifies `Stripe-Signature` using Stripe Java SDK `Webhook.constructEvent()`.

### 2.2 Webhook Deduplication via `payment_events`
Gateways deliver multiple events for a single payment lifecycle (`payment.authorized`, `payment.captured`, `payment.failed`, `refund.processed`) and may retry webhook delivery multiple times.

**Authoritative Deduplication Rule:**  
Every incoming webhook event is registered in the `payment_events` table with a unique constraint on `(provider, gateway_event_id)`:

```sql
CREATE TABLE payment_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID REFERENCES payments(id),
    provider VARCHAR(50) NOT NULL,          -- 'RAZORPAY', 'STRIPE'
    gateway_event_id VARCHAR(255) NOT NULL, -- Unique ID from webhook payload
    gateway_payment_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,       -- 'payment.captured', 'payment.failed'
    payload_hash VARCHAR(64) NOT NULL,
    raw_payload JSONB NOT NULL,
    received_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    error_message TEXT,
    CONSTRAINT uq_payment_event UNIQUE (provider, gateway_event_id)
);
```

### 2.3 Webhook Processing Flow
1. **Verify HMAC Signature:** Reject immediately with HTTP 400 if invalid.
2. **Atomic Registration:**
   ```sql
   INSERT INTO payment_events (id, provider, gateway_event_id, gateway_payment_id, event_type, payload_hash, raw_payload)
   VALUES (gen_random_uuid(), :provider, :gatewayEventId, :gatewayPaymentId, :eventType, :hash, :payloadJson)
   ON CONFLICT (provider, gateway_event_id) DO NOTHING;
   ```
   If 0 rows were inserted, the event is a duplicate delivery: return `HTTP 200 OK` immediately.
3. **Transactional State Machine Execution:**
   - Begin PostgreSQL transaction.
   - Lock payment row: `SELECT * FROM payments WHERE id = :id FOR UPDATE`.
   - Validate state transition against the canonical `PaymentStatus` state machine.
   - Update `payments.status`, `paid_at`, and gateway references.
   - Update `payment_events.processing_status = 'PROCESSED'`.
   - Insert `outbox_events` (`PaymentCompleted` or `PaymentRefunded`).
   - Commit transaction.
4. Return `HTTP 200 OK`.

---

## 3. Canonical Payment Lifecycle & State Normalization

### 3.1 Authoritative Status Enum (`PaymentStatus`)
The platform standardizes on one canonical 7-state lifecycle across all database schemas, APIs, and domain events:

```text
                  ┌─────────────┐
                  │   PENDING   │
                  └──────┬──────┘
                         ├─────────────────────────────────────────┐
                         │ (Payment Authorized / Funds Held)       │ (Payment Failed)
                         ▼                                         ▼
                  ┌─────────────┐                           ┌─────────────┐
                  │ AUTHORIZED  │                           │   FAILED    │
                  └──────┬──────┘                           └─────────────┘
                         │ (Capture Succeeded)
                         ▼
                  ┌─────────────┐
                  │    PAID     │
                  └──────┬──────┘
                         ├────────────────────────┐
                         │ (Partial Refund)       │ (Full Refund)
                         ▼                        ▼
               ┌──────────────────┐      ┌─────────────────┐
               │PARTIALLY_REFUNDED│      │    REFUNDED     │
               └──────────────────┘      └─────────────────┘

* Note on PARTIAL: For milestone/split payments, status is PARTIAL while remaining balance is outstanding.
```

### 3.2 Gateway Normalization Rules
* **Direct / Instant Capture (UPI, Card Direct):** Normalizes `PENDING` $\rightarrow$ `PAID`.
* **Two-Step Authorization & Capture:**
  - Gateway `payment.authorized` $\rightarrow$ Normalizes to `AUTHORIZED`.
  - Gateway `payment.captured` $\rightarrow$ Normalizes to `PAID`.
* **Failed Transactions:** Gateway `payment.failed` $\rightarrow$ Normalizes to `FAILED`.
* **Refund Transactions:**
  - Gateway `refund.processed` with `amount == total_amount` $\rightarrow$ Normalizes to `REFUNDED`.
  - Gateway `refund.processed` with `amount < total_amount` $\rightarrow$ Normalizes to `PARTIALLY_REFUNDED`.

---

## 4. Cash on Delivery (COD) & Field Collection

For customers choosing on-site payment:
1. At booking confirmation: Booking is set to `CONFIRMED` while payment status remains `PENDING`.
2. During visit completion: Field technician records `isCashCollected = true` and `cashAmountCollected`.
3. Backend creates a `payments` record with `payment_method = 'CASH_ON_DELIVERY'`, `status = 'PAID'`, and links to the booking.
4. The Admin ERP reconciliation console tracks cash balances per technician, requiring daily branch cash handovers before shift settlement.

---

## 5. Automated Sequential PDF Invoice Generation

When a payment succeeds or a COD service is completed, the invoice builder executes:

```text
[ Outbox Domain Event: PaymentCompleted OR ServiceCompleted ]
                         │
                         ▼
        [ Spring Boot Invoicing Module ]
                         │ 1. Fetch Booking, Address, Line Items & Tax Breakdown
                         │ 2. Generate Next Sequential Invoice No from PostgreSQL SEQUENCE: INV-YYYY-NNNNN
                         │ 3. Render PDF using OpenPDF Engine
                         │
                         ▼
              [ Upload to Object Storage ]
                         │ (Storage Key: /invoices/2026/09/INV-2026-00042.pdf)
                         │
                         ▼
           [ PostgreSQL Transaction Commit ]
                         │ • INSERT into invoices table
                         │ • INSERT into file_metadata table
                         │ • UPDATE bookings SET invoice_id = ...
                         │ • INSERT into outbox_events (type='InvoiceGenerated')
                         │
                         ▼
             [ RabbitMQ Outbox Relay ] ──► (Sends PDF via Email & FCM push alert)
```

---

## 6. Refund Lifecycle & Credit Notes

* **Cancellation Prior to Dispatch:** Triggers automated full gateway refund API call and marks payment `REFUNDED`.
* **Service Dispute / Partial Refund:** Admin initiates partial refund from Admin Web ERP; backend records negative transaction in `payment_transactions`, transitions payment to `PARTIALLY_REFUNDED`, and generates a credit note PDF.

---

## 7. Payment Gateway Domain Port & Provider Abstraction

To decouple the core `payments` domain module from vendor SDK specifics (Razorpay, Stripe):

```java
package com.pestcontrol.modules.payments.port;

public interface PaymentGatewayPort {
    PaymentOrderResult createOrder(PaymentOrderCommand command);
    boolean verifyWebhookSignature(String rawPayload, Map<String, String> headers);
    GatewayEventPayload parseWebhookEvent(String rawPayload);
    RefundResult processRefund(RefundCommand command);
    PaymentSyncResult fetchPaymentDetails(String gatewayPaymentId);
}
```

* **Provider Adapters:**
  - `RazorpayGatewayAdapter`: Implements `PaymentGatewayPort` using Razorpay Client SDK.
  - `StripeGatewayAdapter`: Implements `PaymentGatewayPort` using Stripe Java SDK.
* **PDF Rendering Standard:** Strictly standardizes on **`OpenPDF`** (LGPL/MPL compliant fork of iText). Alternatives such as proprietary iText versions are forbidden in V1.

