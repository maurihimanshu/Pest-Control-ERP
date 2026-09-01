# Payment & Invoicing Architecture Specification
## Gateway Integration, Webhook Verification & Automated Invoicing

**Document Version:** 1.0.0  
**Payment Gateways:** Razorpay / Stripe (Multi-Gateway Ready)  
**PDF Engine:** OpenPDF / iText inside Spring Boot  
**Transactional Store:** PostgreSQL 16  
**Date:** September 2026  

---

## 1. Payment Processing Architecture

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
         │                                   │ 8. DB Transaction: Payment=PAID    │
         │                                   │ 9. Publish: payment.success        │
         │                                   │                                    │
         │ 10. Polling / WebSocket / FCM     │                                    │
         │◄──────────────────────────────────┤                                    │
```

---

## 2. Webhook Signature Verification & Idempotency

### 2.1 HMAC-SHA256 Signature Verification
Incoming webhooks to `/api/v1/payments/webhooks/{gateway}` are validated before payload deserialization:
* **Razorpay:** Verifies `X-Razorpay-Signature` against the raw HTTP request body using `HmacSHA256` with the webhook secret.
* **Stripe:** Verifies `Stripe-Signature` using Stripe Java SDK `Webhook.constructEvent()`.

### 2.2 Idempotency Safeguards
* Every incoming webhook payload contains a gateway event ID (`event.id` or `payment.id`).
* Spring Boot queries `payments` by `gateway_payment_id`. If the payment record is already in `PAID` status, the webhook returns `HTTP 200 OK` immediately without re-triggering invoices or duplicate events.

---

## 3. Cash on Delivery (COD) & Technician Field Collection

For customers choosing cash or on-site UPI collect:
1. Field technician marks `isCashCollected = true` and enters `cashAmountCollected` during visit completion.
2. Spring Boot creates a `payments` record with `payment_method = 'CASH_ON_DELIVERY'` and `status = 'PAID'`.
3. The Admin ERP reconciliation console tracks cash balances per technician, requiring branch managers to perform daily cash handovers.

---

## 4. Automated PDF Invoice Generation Engine

When a payment succeeds or a service is completed, a RabbitMQ listener executes the invoice builder:

```text
[ RabbitMQ Event: payment.success OR visit.completed ]
                         │
                         ▼
        [ Spring Boot Invoicing Service ]
                         │ 1. Fetch Booking, Address, Line Items & Tax Info
                         │ 2. Generate Next Sequential Invoice No: INV-2026-00042
                         │ 3. Render PDF using OpenPDF Template Engine
                         │
                         ▼
             [ Upload to Object Storage ]
                         │ (Path: /invoices/2026/09/INV-2026-00042.pdf)
                         │
                         ▼
          [ PostgreSQL Transaction Commit ]
                         │ • INSERT into invoices table
                         │ • INSERT into file_metadata table
                         │ • UPDATE bookings.invoice_id
                         │
                         ▼
       [ Emit Event: invoice.generated ] ──► (Sends PDF via Email & FCM alert)
```

---

## 5. Refund Lifecycle & Partial Credits

* **Cancellation Prior to Dispatch:** Triggers automatic full refund via Gateway API.
* **Service Quality Dispute:** Admin can issue a partial or full refund from the Admin Web ERP.
* **Accounting Treatment:** A negative ledger transaction is created under `payment_transactions`, and a credit note PDF is generated.

---

*Governed by PCI-DSS security standards and transactional accounting integrity.*
