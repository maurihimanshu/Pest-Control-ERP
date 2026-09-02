# REST API Specification (OpenAPI / Springdoc)
## Pest Control Enterprise Resource Planning (ERP) Platform

**Document Version:** 1.0.0  
**API Version:** `v1`  
**Base Path:** `/api/v1`  
**Security Scheme:** HTTP Bearer (Firebase ID Token)  
**Date:** September 2026  

---

## 1. REST API Design Standards

### 1.1 Content Negotiation & Standards
* **Protocol:** HTTPS only (TLS 1.3).
* **Data Format:** `application/json; charset=UTF-8` for all request/response bodies.
* **Date-Time & Calendar Semantics:**
  - **UTC Instants (`Instant` / `TIMESTAMPTZ`):** Formatted as ISO 8601 UTC strings with trailing 'Z' (e.g., `2026-09-01T14:30:00Z`). Used for event timestamps, audit logs, creation/update times, and token expirations.
  - **Business Dates (`LocalDate` / `DATE`):** Formatted as ISO 8601 calendar dates `YYYY-MM-DD` (e.g., `2026-09-01`). Used for appointment booking dates, batch expiry dates, and AMC contract schedules.
  - **Local Operating Timezone:** Resolved per agency/branch (`agencies.timezone`, default `Asia/Kolkata`) for calendar scheduling, shift calculation, and daily cron trigger evaluation.
* **Canonical Monetary Contract:**
  - Monetary values are represented in JSON as decimal strings with a 3-letter ISO 4217 currency code. JSON numbers are forbidden for money:
    ```json
    {
      "amount": "1499.00",
      "currency": "INR"
    }
    ```
  - Server-side mapping uses Java `BigDecimal` with scale 2 (`RoundingMode.HALF_UP`). Database columns strictly use PostgreSQL `NUMERIC(12, 2)`.
* **Idempotency Policy (`Idempotency-Key` Header):**
  - **REQUIRED:** All state-mutating `POST` endpoints with externally retryable side effects:
    - `POST /api/v1/bookings`
    - `POST /api/v1/payments/initiate`
    - `POST /api/v1/amc/contracts`
    - `POST /api/v1/dispatch/visits/sync`
    - `POST /api/v1/invoices`
  - **OPTIONAL:** `PUT` / `PATCH` endpoints that are naturally idempotent.
  - **FORBIDDEN / IGNORED:** `GET`, `HEAD`, `DELETE` where HTTP semantics already define safe/idempotent execution.
  - Duplicate requests matching `(agency_id, user_id, request_path, request_hash)` within 24 hours return the exact cached response body without re-execution.

---

## 2. Standardized Response & Error Envelopes

### 2.1 Standard Success Envelope (`ApiResponse<T>`)
```json
{
  "success": true,
  "data": { ... },
  "message": "Resource retrieved successfully",
  "timestamp": "2026-09-01T14:30:00Z",
  "traceId": "c83f9a2b-1029-4b11-a832"
}
```

### 2.2 Standard Paginated Success Envelope (`PagedApiResponse<T>`)
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 0,
    "size": 20,
    "totalElements": 145,
    "totalPages": 8,
    "isLast": false
  },
  "timestamp": "2026-09-01T14:30:00Z",
  "traceId": "c83f9a2b-1029-4b11-a832"
}
```

### 2.3 Standard Error Envelope (`ApiErrorResponse`)
```json
{
  "success": false,
  "errorCode": "BOOKING_SLOT_UNAVAILABLE",
  "message": "Selected time slot is already fully committed for this technician.",
  "errors": [
    {
      "field": "scheduledTimeSlot",
      "rejectedValue": "10:00 AM - 12:00 PM",
      "reason": "Overlaps with existing confirmed visit SV-2026-00042"
    }
  ],
  "timestamp": "2026-09-01T14:30:00Z",
  "traceId": "c83f9a2b-1029-4b11-a832"
}
```

---

## 3. Server-Side Pagination, Filtering & Sorting Conventions

All list endpoints support standard Spring Data `Pageable` parameters:
* `page`: Zero-indexed page number (default `0`).
* `size`: Page size (default `20`, max `100`).
* `sort`: Multi-field sorting (e.g., `sort=scheduledDate,desc&sort=createdAt,asc`).
* Filtering queries: Exact or range matches (e.g., `status=CONFIRMED&fromDate=2026-09-01&toDate=2026-09-30`).

---

## 4. Primary API Endpoint Manifest

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 REST API Endpoint Matrix                                    │
├────────┬───────────────────────────────────────────┬───────────────────┬────────────────────┤
│ Method │ Endpoint Path                             │ Auth Role         │ Description        │
├────────┼───────────────────────────────────────────┼───────────────────┼────────────────────┤
│ POST   │ /api/v1/auth/sync                         │ Authenticated     │ Sync Firebase User │
│ GET    │ /api/v1/customers/me                      │ CUSTOMER          │ Get My Profile     │
│ POST   │ /api/v1/customers/addresses               │ CUSTOMER          │ Add Address        │
│ GET    │ /api/v1/services                          │ Public / All      │ List Catalog       │
│ POST   │ /api/v1/pricing/calculate                 │ Authenticated     │ Compute Cart Rate  │
│ POST   │ /api/v1/bookings                          │ CUSTOMER, ADMIN   │ Create Booking     │
│ GET    │ /api/v1/bookings                          │ DISPATCHER, ADMIN │ Paginated Bookings │
│ GET    │ /api/v1/bookings/{id}                     │ CUSTOMER, ADMIN   │ Booking Details    │
│ POST   │ /api/v1/bookings/{id}/cancel              │ CUSTOMER, ADMIN   │ Cancel Booking     │
│ POST   │ /api/v1/bookings/{id}/reschedule          │ CUSTOMER, ADMIN   │ Reschedule Booking │
│ POST   │ /api/v1/dispatch/work-orders/{id}/assign  │ DISPATCHER, ADMIN │ Assign Technician  │
│ GET    │ /api/v1/dispatch/technicians/me/jobs      │ TECHNICIAN        │ Get Assigned Jobs  │
│ POST   │ /api/v1/dispatch/visits/{id}/accept       │ TECHNICIAN        │ Accept Job         │
│ POST   │ /api/v1/dispatch/visits/{id}/start        │ TECHNICIAN        │ Start Job          │
│ POST   │ /api/v1/dispatch/visits/{id}/complete     │ TECHNICIAN        │ Complete Field Job │
│ POST   │ /api/v1/dispatch/visits/sync              │ TECHNICIAN        │ Offline Batch Sync │
│ POST   │ /api/v1/payments/initiate                 │ CUSTOMER          │ Init Payment Intent│
│ POST   │ /api/v1/payments/webhooks/{gateway}       │ Public (HMAC)     │ Gateway Webhook    │
│ GET    │ /api/v1/invoices/{id}/download            │ CUSTOMER, ADMIN   │ Get PDF Invoice    │
│ GET    │ /api/v1/inventory/chemicals               │ ADMIN, AGENCY_MANAGER │ Chemical Inventory │
│ POST   │ /api/v1/inventory/batches                 │ ADMIN, AGENCY_MANAGER │ Receive New Batch  │
│ POST   │ /api/v1/amc/contracts                     │ ADMIN, CUSTOMER   │ Create AMC Contract│
│ GET    │ /api/v1/reports/dashboard-kpis            │ ADMIN, AGENCY_MANAGER │ Management KPIs    │
│ GET    │ /api/v1/audit/logs                        │ SUPER_ADMIN       │ Query Audit Logs   │
└────────┴───────────────────────────────────────────┴───────────────────┴────────────────────┘
```

---

## 5. Representative API Contract Specifications

### 5.1 Dynamic Price Calculation (`POST /api/v1/pricing/calculate`)

#### Request Body:
```json
{
  "serviceId": "7a3e9c12-5b8d-4a11-b012-3c8f9e012345",
  "pricingTier": "2 BHK",
  "areaSqFt": null,
  "addOnServiceIds": [
    "2b1f8e43-9a11-4c22-d033-5e7a8b9c0123"
  ],
  "couponCode": "WELCOME20",
  "pincode": "700091"
}
```

#### Response Body (`200 OK`):
```json
{
  "success": true,
  "data": {
    "basePrice": "1499.00",
    "addOnTotal": "300.00",
    "subtotal": "1799.00",
    "discountAmount": "359.80",
    "discountDescription": "20% off with coupon WELCOME20",
    "taxableAmount": "1439.20",
    "taxAmount": "259.06",
    "taxRatePercentage": "18.00",
    "totalPayableAmount": "1698.26",
    "currency": "INR"
  },
  "message": "Pricing calculated successfully",
  "timestamp": "2026-09-01T14:30:00Z",
  "traceId": "req-982374"
}
```

---

### 5.2 Create Booking (`POST /api/v1/bookings`)

#### Request Headers:
`Idempotency-Key: 9b2d8e31-4c12-4d56-a789-0123456789ab`

#### Request Body:
```json
{
  "customerAddressId": "5f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "scheduledDate": "2026-09-12",
  "scheduledTimeSlot": "10:00 AM - 12:00 PM",
  "couponCode": "WELCOME20",
  "customerNotes": "Call before arrival. Infestation in kitchen.",
  "items": [
    {
      "serviceId": "7a3e9c12-5b8d-4a11-b012-3c8f9e012345",
      "pricingTier": "2 BHK",
      "quantity": 1
    }
  ]
}
```

#### Response Body (`201 Created`):
```json
{
  "success": true,
  "data": {
    "bookingId": "3b7c8d9e-0f1a-2b3c-4d5e-6f7a8b9c0d1e",
    "bookingNumber": "BK-2026-00042",
    "status": "CONFIRMED",
    "paymentStatus": "PENDING",
    "scheduledDate": "2026-09-12",
    "scheduledTimeSlot": "10:00 AM - 12:00 PM",
    "totalPayableAmount": "1698.26",
    "workOrderId": "8f9a0b1c-2d3e-4f5a-6b7c-8d9e0f1a2b3c",
    "workOrderNumber": "WO-2026-00042"
  },
  "message": "Booking created and slot confirmed",
  "timestamp": "2026-09-01T14:30:00Z",
  "traceId": "req-982375"
}
```

---

### 5.3 Technician Field Completion (`POST /api/v1/dispatch/visits/{id}/complete`)

#### Request Body:
```json
{
  "offlineEventId": "evt_local_9837428",
  "actualCompletionTime": "2026-09-12T11:45:00Z",
  "technicianNotes": "Gel applied across all kitchen cabinets and drain openings.",
  "customerSignatureFileId": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
  "beforePhotoFileIds": [
    "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
  ],
  "afterPhotoFileIds": [
    "2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e"
  ],
  "materialsUsed": [
    {
      "chemicalBatchId": "4c5d6e7f-8a9b-0c1d-2e3f-4a5b6c7d8e9f",
      "quantityUsed": "50.00",
      "dosageRate": "10g / cabinet",
      "targetPest": "German Cockroach"
    }
  ],
  "isCashCollected": true,
  "cashAmountCollected": "1698.26"
}
```

#### Response Body (`200 OK`):
```json
{
  "success": true,
  "data": {
    "serviceVisitId": "1f2e3d4c-5b6a-7f8e-9d0c-1b2a3f4e5d6c",
    "visitNumber": "SV-2026-00042",
    "status": "COMPLETED",
    "workOrderStatus": "COMPLETED",
    "invoiceGenerated": true,
    "invoiceNumber": "INV-2026-00042"
  },
  "message": "Service visit completed and invoice triggered",
  "timestamp": "2026-09-12T11:45:05Z",
  "traceId": "req-982376"
}
```

---

*All REST endpoints are documented via Springdoc OpenAPI at `/swagger-ui.html`.*
