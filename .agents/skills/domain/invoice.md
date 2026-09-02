---
name: invoice
description: Generating and managing tax invoices for bookings.
category: domain
triggers:
  - Generate PDF invoice
  - Payment completed
inputs:
  - Payment success events
outputs:
  - PDF Invoice generation
dependencies:
  - domain/payment
  - domain/booking
related_skills:
  - backend/object-storage-integration
---

# Skill: Invoice Domain

## Purpose
To generate, store, and track legally compliant tax invoices for completed or paid bookings within the ERP.

## When to Use / When NOT to Use
**Use When:** A customer needs a receipt, or a payment is successfully completed.
**NOT to Use:** For internal cost tracking or proforma estimations (use Booking/Pricing).

## Required Context
Invoice generation must be reliable, idempotent, and legally compliant (sequential numbering).

## Domain Rules & Constraints
1. **Sequential Numbering:** Invoice numbers (e.g., `INV-2024-0001`) use PostgreSQL `invoice_seq` for unique, monotonically allocated values. Gaps after rollback are expected and must never be reused.
2. **Idempotency:** If the `PaymentCompletedEvent` is received twice, the system must return the URL of the already generated invoice, not create a new one.
3. **Storage:** The generated PDF is uploaded to Object Storage (S3/GCS). The database stores the metadata and the URI.

## Entity Structure
*   `id` UUID
*   `booking_id` UUID
*   `invoice_number` VARCHAR (Unique)
*   `amount` DECIMAL
*   `tax_amount` DECIMAL
*   `pdf_url` TEXT
*   `status` VARCHAR (GENERATED, SENT, CANCELLED)
*   `created_at`

## Spring Service Methods
*   `Invoice generateInvoice(UUID bookingId)`
*   `String getInvoicePdfUrl(String invoiceNumber)`

## Database Considerations
*   `invoice_number` must have a `UNIQUE` constraint.
*   Creation of the invoice and incrementing the sequence must be in the same transaction.

## RabbitMQ Events
*   Consumed: `PaymentCompletedEvent` (or sometimes `BookingCompletedEvent` for post-paid corporate accounts).
*   Published: `InvoiceGeneratedEvent` -> Consumed by Notification Service to email the PDF link to the customer.

## Validation Checklist
- [ ] Is PDF generation triggered asynchronously via RabbitMQ?
- [ ] Is OpenPDF (or similar Java library) used correctly without memory leaks?
- [ ] Are invoice numbers unique and monotonically allocated, with any sequence gaps retained?
- [ ] Is the PDF securely stored in an S3 bucket with appropriate access controls (presigned URLs)?

## Common Mistakes
*   Generating the PDF synchronously in the main web request thread, causing timeouts.
*   Generating multiple invoices for the same booking due to lack of idempotency.
*   Storing raw PDF byte arrays in the PostgreSQL database.

## Related Skills
- `domain/payment`
- `backend/object-storage-integration`
