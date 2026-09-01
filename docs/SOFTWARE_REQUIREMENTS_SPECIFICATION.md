# Software Requirements Specification (SRS)
## Pest Control Enterprise Resource Planning (ERP) System

**Document Version:** 1.0.0  
**Status:** Client Ready / Specification Baseline  
**Date:** September 2026  
**Target Systems:** Customer Android App, Technician Android App, Admin Web ERP Dashboard, Firebase Cloud Backend  

---

## Table of Contents

1. [Executive Summary & Purpose](#1-executive-summary--purpose)
2. [Overall System Architecture](#2-overall-system-architecture)
3. [User Roles & RBAC Permission Matrix](#3-user-roles--rbac-permission-matrix)
4. [Functional Requirements (Module Breakdown)](#4-functional-requirements-module-breakdown)
   - [4.1 Authentication & Profile Management](#41-authentication--profile-management)
   - [4.2 Service Catalog & Dynamic Pricing Engine](#42-service-catalog--dynamic-pricing-engine)
   - [4.3 Booking & State Machine Engine](#43-booking--state-machine-engine)
   - [4.4 Field Technician Operations & Offline Sync](#44-field-technician-operations--offline-sync)
   - [4.5 Payment Gateway, Invoicing & Financial Transactions](#45-payment-gateway-invoicing--financial-transactions)
   - [4.6 Admin Operations, Dispatching & Resource Management](#46-admin-operations-dispatching--resource-management)
   - [4.7 Agency / Branch Management](#47-agency--branch-management)
   - [4.8 Expense & Revenue Management](#48-expense--revenue-management)
   - [4.9 AMC (Annual Maintenance Contracts) & Recurring Services](#49-amc-annual-maintenance-contracts--recurring-services)
   - [4.10 Feedback, Ratings & Support Ticketing](#410-feedback-ratings--support-ticketing)
   - [4.11 Notification & Communications Engine](#411-notification--communications-engine)
   - [4.12 Audit Logging & Compliance](#412-audit-logging--compliance)
5. [Cloud Firestore Data Models & Schema Design](#5-cloud-firestore-data-models--schema-design)
6. [Cloud Functions API & State Machine Specifications](#6-cloud-functions-api--state-machine-specifications)
7. [Security & Authorization Architecture](#7-security--authorization-architecture)
8. [Non-Functional Requirements (NFR)](#8-non-functional-requirements-nfr)
9. [Project Phasing & Scope Matrix (MVP vs Phase 2)](#9-project-phasing--scope-matrix-mvp-vs-phase-2)

---

# 1. Executive Summary & Purpose

The **Pest Control ERP Platform** is a unified, multi-platform software suite engineered to digitize and automate the entire operational lifecycle of a modern pest control enterprise.

The platform coordinates interactions among four primary stakeholder groups:
1. **Customers:** Discover pest control services, request quotes, schedule visits, make payments, track technician status, and access service histories.
2. **Technicians (Field Force):** Receive job assignments, navigate to client sites, execute treatment protocols offline/online, capture evidence (before/after photos), record chemical usage, and obtain customer sign-offs.
3. **Agency/Branch Managers:** Monitor local technicians, manage branch inventory, and track regional revenue/commissions.
4. **Central Administrators / Executives:** Control service catalogs, manage dynamic pricing, dispatch technicians, audit financial entries, reconcile accounts, and analyze operational KPIs.

---

# 2. Overall System Architecture

```text
                               ┌──────────────────────────────────────────────┐
                               │             Firebase Backend Layer           │
                               │                                              │
                               │  • Firebase Authentication (Custom Claims)   │
                               │  • Cloud Firestore (NoSQL Document Store)    │
                               │  • Cloud Storage (Encrypted Media/PDFs)      │
                               │  • Cloud Functions (TypeScript Node.js 20)   │
                               │  • Firebase Cloud Messaging (FCM Topics)     │
                               │  • Firebase App Check (Integrity Guard)      │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┼──────────────────────────────┐
                       │                              │                              │
                       ▼                              ▼                              ▼
        ┌─────────────────────────────┐┌─────────────────────────────┐┌─────────────────────────────┐
        │    Customer Android App     ││    Technician Android App   ││       Admin Web ERP         │
        ├─────────────────────────────┤├─────────────────────────────┤├─────────────────────────────┤
        │ • Native Java 21            ││ • Native Java 21            ││ • React 18 + TypeScript     │
        │ • Gradle Kotlin DSL         ││ • Gradle Kotlin DSL         ││ • Vite + TailwindCSS        │
        │ • MVVM + Android Jetpack    ││ • Offline SQLite (Room DB)  ││ • Ant Design / Shadcn UI    │
        │ • Retrofit + Firebase SDK   ││ • WorkManager Background Q  ││ • Firebase Web SDK v10      │
        │ • Google Maps SDK           ││ • CameraX + Image Compressor││ • Recharts / Chart.js       │
        └─────────────────────────────┘└─────────────────────────────┘└─────────────────────────────┘
```

### Architectural Principles:
1. **Zero-Trust Client Access:** Price calculation, booking confirmation, invoice generation, and status progression must occur strictly inside **Firebase Cloud Functions** and Firestore Transactions.
2. **Offline-First Field App:** Field technicians must be able to perform 100% of physical service check-in, execution, material logging, and customer sign-off without an active internet connection.
3. **Audit Trail Immutability:** Sensitive financial events, booking state transitions, and administrative overrides are appended to an immutable `audit_logs` and `booking_events` collection.

---

# 3. User Roles & RBAC Permission Matrix

System access is enforced using **Firebase Auth Custom Claims** (`token.claims.role`) checked directly in Firestore Security Rules and Cloud Functions.

| Capability / Module | Customer | Field Technician | Agency Manager | Dispatcher / Operations | Super Admin |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Browse Services & Rates | ✅ | ❌ | ✅ | ✅ | ✅ |
| Create Self-Service Booking | ✅ | ❌ | ❌ | ✅ (Manual) | ✅ (Manual) |
| View Own Bookings / Tasks | ✅ (Own) | ✅ (Assigned) | ✅ (Branch) | ✅ (All) | ✅ (All) |
| Accept / Reject Assigned Job | ❌ | ✅ | ❌ | ❌ | ❌ |
| Start Service & Log Chemicals | ❌ | ✅ | ❌ | ❌ | ✅ (Override) |
| Manual Dispatch & Reassignment | ❌ | ❌ | ✅ (Branch) | ✅ | ✅ |
| Manage Service Catalog & Prices| ❌ | ❌ | ❌ | ❌ | ✅ |
| Create Coupons & Discounts | ❌ | ❌ | ❌ | ❌ | ✅ |
| Log Operating Expenses | ❌ | ❌ | ✅ (Branch) | ❌ | ✅ |
| View Executive Revenue & P&L | ❌ | ❌ | ❌ | ❌ | ✅ |
| Manage Employees & Agencies | ❌ | ❌ | ✅ (Branch staff)| ❌ | ✅ |
| View System Audit Logs | ❌ | ❌ | ❌ | ❌ | ✅ |

---

# 4. Functional Requirements (Module Breakdown)

## 4.1 Authentication & Profile Management

### Scope:
* **Customer App:** Phone Number + OTP (Primary) with Google Sign-In and Email/Password fallback.
* **Technician App:** Corporate Employee ID / Mobile + Secure PIN with device UUID binding.
* **Admin Web Dashboard:** Corporate Email + Password + Multi-Factor Authentication (MFA).

### User Stories & Acceptance Criteria:
* **US-1.1:** As a customer, I want to authenticate via OTP so I can quickly place a booking without remembering passwords.
  * *Acceptance Criteria:* OTP delivery within 15 seconds; automatic SMS verification hook on Android; maximum 3 retries before a 10-minute cooldown.
* **US-1.2:** As an admin, I want to deactivate a technician's account immediately upon termination so they cannot access customer address information.
  * *Acceptance Criteria:* Changing technician status to `INACTIVE` in Admin ERP revokes their Firebase refresh token instantly.

---

## 4.2 Service Catalog & Dynamic Pricing Engine

### Scope:
* Hierarchical catalog: **Categories** (e.g., Residential, Commercial, Industrial) $\rightarrow$ **Services** (e.g., Cockroach Gel Treatment, Termite Subterranean Piping, Bedbug Heat Treatment).
* Configurable Pricing Models:
  1. **Fixed Flat Fee:** (e.g., Mosquito fogging standard lot = ₹2,000 / $80).
  2. **Area / Dimension-Based:** (e.g., ₹1.50 per sq. ft. for commercial factories).
  3. **Configuration-Based:** (e.g., 1 BHK, 2 BHK, 3 BHK, Villa, Commercial Office).
  4. **Add-on Treatment Options:** (e.g., Kitchen Drain Deep Cleansing, Odorless Spray Upgrade).

### Calculation Formula in Cloud Function:
$$\text{Base Amount} = \text{Unit Price} \times \text{Quantity / Area}$$
$$\text{Subtotal} = \text{Base Amount} + \sum \text{Add-ons}$$
$$\text{Discounted Subtotal} = \max(0, \text{Subtotal} - \text{Discount Calculated})$$
$$\text{Tax Amount} = \text{Discounted Subtotal} \times \text{Applicable Tax Rate}$$
$$\text{Final Payable} = \text{Discounted Subtotal} + \text{Tax Amount}$$

---

## 4.3 Booking & State Machine Engine

### Standard Booking State Lifecycle:

```text
[ DRAFT / CART ]
       │
       ▼ (Customer Checkout)
  [ PENDING ] ──────────────► [ PAYMENT_FAILED ]
       │ (Payment Success / COD Selected)
       ▼
 [ CONFIRMED ]
       │ (Auto or Manual Dispatch)
       ▼
  [ ASSIGNED ] ─────────────► [ REASSIGNED ]
       │ (Technician Accepts)
       ▼
[ TECHNICIAN_ACCEPTED ]
       │ (Technician departs)
       ▼
 [ ON_THE_WAY ]
       │ (Technician arrives at customer premises)
       ▼
 [ ARRIVED_ON_SITE ]
       │ (Service checklist started)
       ▼
[ SERVICE_IN_PROGRESS ]
       │ (Chemicals logged, before/after photos captured, customer sign-off)
       ▼
[ SERVICE_COMPLETED ]
       │ (Final payment reconciliation & invoice generated)
       ▼
   [ CLOSED ]
```

### Exception States:
* `CANCELLED_BY_CUSTOMER` (Allowed only prior to `ON_THE_WAY`).
* `CANCELLED_BY_ADMIN` (Includes mandatory refund trigger Cloud Function).
* `RESCHEDULED` (Transfers slot and retains payment token).
* `NO_SHOW_CUSTOMER` / `UNABLE_TO_ACCESS` (Technician records arrival with GPS & photo proof).

---

## 4.4 Field Technician Operations & Offline Sync

### Offline Architecture:
Technicians operate frequently in basements, elevator shafts, and remote compounds.
1. **Local Queue (Room SQLite):** Actions performed offline (`ARRIVE`, `START_JOB`, `LOG_CHEMICAL`, `COMPLETE_JOB`) are saved locally with a monotonic timestamp and cryptographically signed payload.
2. **Image Staging:** Photos captured via CameraX are compressed to $< 500\text{ KB}$ WebP locally and stored in the app sandbox.
3. **Background Sync:** Android `WorkManager` triggers when network connectivity (`NetworkCapabilities.NET_CAPABILITY_INTERNET`) is re-established, executing requests in chronological order.

### Field Verification Checklist:
* **Pre-Service Inspection Checklist** (Infestation level: Low/Medium/Severe).
* **Chemical / Material Consumption Log** (Chemical Name, Batch No., Volume used in ml/g).
* **Before & After Photos** (Timestamped and geotagged).
* **Digital Sign-off:** Customer digital signature capture on technician screen or OTP verification code sent to customer mobile.

---

## 4.5 Payment Gateway, Invoicing & Financial Transactions

### Supported Payment Modes:
1. **Online Pre-payment:** Gateway SDK integration (Razorpay / Stripe / UPI / Card / NetBanking).
2. **Cash on Delivery (COD) / Collect after Service:** Technician collects cash/UPI at completion; technician app flags `CASH_COLLECTED` requiring admin daily reconciliation.
3. **Post-paid Corporate Invoice (Net 30/60):** For commercial clients with approved credit terms.

### Invoicing Specifications:
* System generates an immutable, tamper-proof **PDF Invoice** upon reaching `SERVICE_COMPLETED` or `PAYMENT_COMPLETED`.
* Sequential invoice numbering sequence enforced via Firestore atomic counters: `INV-2026-00001`.
* Direct PDF delivery to customer email and accessible in-app.

---

## 4.6 Admin Operations, Dispatching & Resource Management

### Features:
* **Interactive Dispatch Board (Gantt & Map View):** Real-time visibility into all bookings by date, time slot, status, and technician schedule.
* **Intelligent Assignment Recommendation Engine:** Ranks technicians based on:
  1. Proximity to customer GPS.
  2. Matching skill matrix (e.g., Termite Drilling certification vs General Fumigation).
  3. Workload balancing (preventing double-booking).
* **Manual Override Console:** Emergency reassignment with automated FCM notifications to both old and new technicians.

---

## 4.7 Agency / Branch Management

### Scope:
* Multi-branch operations where local agencies manage regional territory.
* Separation of customer databases, service areas (by Postal/Pincode boundary), and workforce.
* Agency Commission Tracking (e.g., $15\%$ gross revenue per fulfilled job or fixed fee).

---

## 4.8 Expense & Revenue Management

### Operational Accounting Module:
* **Expense Tracking Categories:** Technician Conveyance / Fuel, Chemical Purchases, Equipment Servicing, Marketing, Branch Rent, Utilities.
* **Receipt Capture:** Upload invoice/receipt directly from Admin Web app.
* **Profitability Dashboard:** Real-time calculation:
  $$\text{Net Operational Margin} = \text{Gross Realized Service Revenue} - (\text{Chemical COGS} + \text{Payouts/Commissions} + \text{Direct Expenses})$$

---

## 4.9 AMC (Annual Maintenance Contracts) & Recurring Services

### Contract Structure:
* **Standard AMC Package Types:**
  * Quarterly Treatment (4 visits / year).
  * Bi-Monthly Treatment (6 visits / year).
  * Monthly Commercial Sanitization (12 visits / year).
* **Automated Child Booking Generator:** A Cloud Scheduler cron job scans active AMCs 7 days before the next due date and automatically creates a pre-scheduled booking in `PENDING_ASSIGNMENT` status.

---

## 4.10 Feedback, Ratings & Support Ticketing

* Post-service prompt on Customer App (1–5 Stars + Multi-criteria ratings: *Punctuality, Chemical Odor, Professionalism, Cleanliness*).
* Ratings $< 3$ stars automatically generate an urgent **P1 Support Ticket** on the Admin ERP dashboard with automated manager alert.
* In-app support ticket submission with photo uploads for pest recurrence under warranty.

---

## 4.11 Notification & Communications Engine

* **Firebase Cloud Messaging (FCM):** Push notifications for status changes.
* **Transactional SMS & WhatsApp Notifications:** For booking confirmations, OTPs, technician arrival alerts, and invoice download links.
* **FCM Topic Structure:**
  * `customer_{customerId}`: Personal booking updates.
  * `technician_{employeeId}`: New job broadcasts and reassignment alerts.
  * `agency_{agencyId}_dispatch`: Branch-level alerts.
  * `admin_alerts`: High-priority operational failures (e.g., payment failure, SLA breach).

---

## 4.12 Audit Logging & Compliance

* Every data mutation (status changes, price alterations, discount creation, manual reassignments) creates an append-only document in `audit_logs`.
* **Audit Payload Example:**
  ```json
  {
    "logId": "aud_92837482",
    "timestamp": "2026-09-01T17:50:00Z",
    "actorId": "usr_admin_01",
    "actorRole": "SUPER_ADMIN",
    "action": "BOOKING_MANUAL_REASSIGNMENT",
    "entityType": "bookings",
    "entityId": "bk_10928",
    "changes": {
      "previousTechnicianId": "emp_04",
      "newTechnicianId": "emp_09",
      "reason": "Emergency vehicle breakdown"
    }
  }
  ```

---

# 5. Cloud Firestore Data Models & Schema Design

```text
/users/{userId}
    ├── profile: { name, email, phone, role, status, createdAt }
    └── addresses/{addressId} [Subcollection]

/technicians/{technicianId}
    ├── details: { employeeCode, agencyId, skills[], rating, isAvailable, activeJobId }
    └── attendance/{date} [Subcollection]

/agencies/{agencyId}
    └── details: { name, code, contactEmail, commissionRate, servicePincodes[] }

/services/{serviceId}
    └── details: { title, description, categoryId, pricingType, basePrice, durationMinutes, requiredSkills[] }

/pricing_rules/{ruleId}
    └── details: { serviceId, unitType, tierPricing[], isActive }

/coupons/{couponCode}
    └── details: { discountType, value, maxDiscount, minBookingValue, validUntil, usageCount, perUserLimit }

/bookings/{bookingId}
    ├── customerId: string
    ├── agencyId: string
    ├── assignedTechnicianId: string | null
    ├── status: string (Enum)
    ├── schedule: { date: string, timeSlot: string, estimatedDurationMinutes: number }
    ├── address: { addressLine, city, pincode, lat, lng }
    ├── lineItems: [
    │     { serviceId, title, pricingTier, quantity, unitPrice, lineTotal }
    │   ]
    ├── pricingBreakdown: { subtotal, discountAmount, taxAmount, finalPayable }
    ├── payment: { status, mode, transactionId, invoiceId }
    ├── executionLog: {
    │     arrivedAt, startedAt, completedAt,
    │     materialsUsed: [ { chemicalName, batchNumber, quantityUsed, unit } ],
    │     beforePhotos: [ url ], afterPhotos: [ url ],
    │     customerSignatureUrl: string
    │   }
    ├── metadata: { createdAt, updatedAt, amcContractId }
    └── events/{eventId} [Subcollection for granular audit trail]

/invoices/{invoiceId}
    └── details: { invoiceNumber, bookingId, customerId, amount, pdfUrl, generatedAt }

/expenses/{expenseId}
    └── details: { agencyId, category, amount, date, receiptUrl, approvedBy }

/amc_contracts/{contractId}
    └── details: { customerId, serviceId, totalVisits, completedVisits, startDate, endDate, billingStatus }

/support_tickets/{ticketId}
    └── details: { customerId, bookingId, subject, status, priority, messages[] }

/audit_logs/{logId}
    └── details: { timestamp, actorId, actorRole, action, entityType, entityId, changes }
```

---

# 6. Cloud Functions API & State Machine Specifications

All state changes and financial operations execute via callable HTTPS Cloud Functions or Firestore Triggers:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Cloud Functions Manifest                                    │
├──────────────────────────────┬──────────────────┬───────────────────────────────────────────┤
│ Function Name                │ Trigger Type     │ Description                               │
├──────────────────────────────┼──────────────────┼───────────────────────────────────────────┤
│ calculateCartPricing         │ Callable HTTPS   │ Validates coupon, computes tax & totals   │
│ createBookingIntent          │ Callable HTTPS   │ Locks slot, initiates payment gateway     │
│ handlePaymentWebhook         │ Webhook (HTTPS)  │ Idempotent payment verification & status  │
│ assignTechnicianToBooking    │ Callable HTTPS   │ Verifies availability, assigns & pushes   │
│ updateTechnicianJobState     │ Callable HTTPS   │ Enforces state machine transitions        │
│ generateInvoicePdfOnComplete │ Firestore Trigger│ Triggers PDF builder & saves Cloud Storage│
│ amcScheduledVisitCron        │ Pub/Sub Schedule │ Daily cron creating recurring jobs        │
│ aggregateDailyFinancials     │ Pub/Sub Schedule │ Computes daily revenue & metrics rollups  │
└──────────────────────────────┴──────────────────┴───────────────────────────────────────────┘
```

---

# 7. Security & Authorization Architecture

### Firestore Security Rules Blueprint:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    function hasRole(role) {
      return isAuthenticated() && request.auth.token.role == role;
    }
    function isSuperAdmin() {
      return hasRole('SUPER_ADMIN');
    }
    function isDispatcher() {
      return hasRole('SUPER_ADMIN') || hasRole('DISPATCHER');
    }
    function isAssignedTechnician(techId) {
      return hasRole('TECHNICIAN') && request.auth.uid == techId;
    }
    function isCustomerOwner(custId) {
      return hasRole('CUSTOMER') && request.auth.uid == custId;
    }

    // Bookings collection security
    match /bookings/{bookingId} {
      allow read: if isDispatcher() || 
                     (hasRole('CUSTOMER') && resource.data.customerId == request.auth.uid) ||
                     (hasRole('TECHNICIAN') && resource.data.assignedTechnicianId == request.auth.uid);
      
      // Strict: Creation and sensitive updates must pass via Cloud Functions
      allow create: if false; 
      allow update: if isDispatcher() || (isAssignedTechnician(resource.data.assignedTechnicianId));
      allow delete: if isSuperAdmin();
    }

    // Invoices and financial audit records are immutable
    match /invoices/{invoiceId} {
      allow read: if isDispatcher() || resource.data.customerId == request.auth.uid;
      allow write: if false; // Only Cloud Functions using Admin SDK
    }

    match /audit_logs/{logId} {
      allow read: if isSuperAdmin();
      allow write: if false; // Strictly append-only via Admin SDK
    }
  }
}
```

---

# 8. Non-Functional Requirements (NFR)

| Parameter | Requirement Target | Implementation Strategy |
| :--- | :--- | :--- |
| **Response Latency** | $< 500\text{ ms}$ for 95% of queries | Firestore composite indexing and cached CDN endpoints for catalogs. |
| **Offline Durability** | Zero data loss for technician logs | Room SQLite queue with transactional write-ahead logging. |
| **Data Security** | End-to-End Encryption in Transit & Rest | TLS 1.3, AES-256 for Firestore & Cloud Storage, App Check with DeviceCheck/SafetyNet. |
| **High Availability** | 99.95% uptime SLA | Multi-region Cloud Functions and Firestore replication. |
| **Scalability** | Support 10,000+ bookings / day | Asynchronous decoupling via Cloud Tasks / PubSub for invoice generation and messaging. |

---

# 9. Project Phasing & Scope Matrix (MVP vs Phase 2)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              Scope Phasing Matrix                                      │
├────────────────────────────────────────────┬─────────────┬─────────────┬───────────────┤
│ Module / Capability                        │ MVP Phase 1 │ Phase 2     │ Phase 3 (Adv) │
├────────────────────────────────────────────┼─────────────┼─────────────┼───────────────┤
│ Customer App (Booking, Catalog, Payment)   │     ✅      │      -      │       -       │
│ Technician App (Job List, Checklist, Photos│     ✅      │      -      │       -       │
│ Technician Offline Sync Queue              │     ✅      │      -      │       -       │
│ Admin ERP Web Dashboard                    │     ✅      │      -      │       -       │
│ Manual Dispatch & Assignment               │     ✅      │      -      │       -       │
│ Online Gateway + Cash on Delivery Payments │     ✅      │      -      │       -       │
│ Automated PDF Invoicing                    │     ✅      │      -      │       -       │
│ Push Notifications (FCM)                   │     ✅      │      -      │       -       │
│ Basic Expense & Daily Revenue Tracking     │     ✅      │      -      │       -       │
├────────────────────────────────────────────┼─────────────┼─────────────┼───────────────┤
│ Live GPS Technician Tracking on Map        │      -      │     ✅      │       -       │
│ Automated AI Dispatch & Route Optimization │      -      │     ✅      │       -       │
│ AMC / Subscription Recurring Generator     │      -      │     ✅      │       -       │
│ Agency Multi-Branch Sub-Portals            │      -      │     ✅      │       -       │
│ Customer WhatsApp Bot Integration          │      -      │     ✅      │       -       │
│ Advanced P&L, Inventory & Chemical COGS    │      -      │     ✅      │       -       │
├────────────────────────────────────────────┼─────────────┼─────────────┼───────────────┤
│ IoT Rodent Trap Integration                │      -      │      -      │      ✅       │
│ Barcode/QR Scanning on Bait Stations       │      -      │      -      │      ✅       │
└────────────────────────────────────────────┴─────────────┴─────────────┴───────────────┘
```

---

*Document compiled for review and client sign-off prior to codebase scaffolding.*
