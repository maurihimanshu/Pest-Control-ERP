# Software Requirements Specification (SRS)
## Pest Control Enterprise Resource Planning (ERP) System

**Document Version:** 3.0.0  
**Target Systems:** Customer Android App, Technician Android App, Admin Web ERP Dashboard, Backend REST API  
**Primary System of Record:** PostgreSQL 16  
**External Supporting Services:** Firebase Authentication (Identity Provider), Firebase Cloud Messaging (Push Delivery), Payment Gateways (Razorpay/Stripe), Maps & Geocoding Provider, Transactional SMS & Email Providers  
**Architecture Reference:** Modular Monolith ([`docs/ARCHITECTURE.md`](ARCHITECTURE.md), [`docs/MODULE_CATALOG.md`](MODULE_CATALOG.md))  
**Date:** September 2026  

---

## Table of Contents

1. [Executive Summary & Purpose](#1-executive-summary--purpose)
2. [Scope of the System](#2-scope-of-the-system)
3. [User Classes & Stakeholder Personas](#3-user-classes--stakeholder-personas)
4. [Role-Based Access Control (RBAC) Requirements](#4-role-based-access-control-rbac-requirements)
5. [3-Tier Operational Domain Concept](#5-3-tier-operational-domain-concept)
6. [Functional Requirements](#6-functional-requirements)
   - [6.1 Authentication & User Management](#61-authentication--user-management)
   - [6.2 Customer & Address Management](#62-customer--address-management)
   - [6.3 Service Catalog & Pricing Engine](#63-service-catalog--pricing-engine)
   - [6.4 Commercial Bookings & Slot Reservations](#64-commercial-bookings--slot-reservations)
   - [6.5 Dispatch, Work Orders & Field Scheduling](#65-dispatch-work-orders--field-scheduling)
   - [6.6 Field Operations & Offline Mobile Execution](#66-field-operations--offline-mobile-execution)
   - [6.7 Payments, Cash Collection & Invoicing](#67-payments-cash-collection--invoicing)
   - [6.8 Inventory & Chemical Management](#68-inventory--chemical-management)
   - [6.9 Branch Expense & Operational Accounting](#69-branch-expense--operational-accounting)
   - [6.10 Annual Maintenance Contracts (AMC)](#610-annual-maintenance-contracts-amc)
   - [6.11 Customer Support, Ratings & Escalations](#611-customer-support-ratings--escalations)
   - [6.12 Notifications & Alerts Engine](#612-notifications--alerts-engine)
   - [6.13 Audit Trails & Compliance](#613-audit-trails--compliance)
   - [6.14 Executive Reporting & Analytics](#614-executive-reporting--analytics)
7. [Non-Functional Requirements (NFR)](#7-non-functional-requirements-nfr)
   - [7.1 Performance & Latency](#71-performance--latency)
   - [7.2 Security & Data Protection](#72-security--data-protection)
   - [7.3 Reliability & Availability](#73-reliability--availability)
   - [7.4 Offline Durability & Data Integrity](#74-offline-durability--data-integrity)
8. [Phased Release Scope](#8-phased-release-scope)

---

# 1. Executive Summary & Purpose

The **Pest Control ERP Platform** is an enterprise software solution designed to digitize, streamline, and coordinate end-to-end pest management operations across commercial and residential customer segments.

The platform provides a centralized, authoritative operational backbone connecting customers, field technicians, branch dispatchers, accountants, and executive administrators into a single unified operating model.

**Authoritative Requirements Baseline:**  
This document specifies the pure functional and non-functional requirements for the platform. Detailed technical design, database schemas, message broker topology, and concurrency mechanics are defined in the companion architecture specifications:
- System & Component Architecture: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
- Domain Module Catalog: [`docs/MODULE_CATALOG.md`](MODULE_CATALOG.md)
- Concurrency, Locking & Idempotency: [`docs/CONCURRENCY_AND_IDEMPOTENCY.md`](CONCURRENCY_AND_IDEMPOTENCY.md)
- Payment & Invoicing Architecture: [`docs/PAYMENT_ARCHITECTURE.md`](PAYMENT_ARCHITECTURE.md)
- Relational Database Design: [`docs/DATABASE_DESIGN.md`](DATABASE_DESIGN.md)
- Domain Model & Lifecycle State Machines: [`docs/DOMAIN_MODEL.md`](DOMAIN_MODEL.md), [`docs/BOOKING_STATE_MACHINE.md`](BOOKING_STATE_MACHINE.md)

---

# 2. Scope of the System

The platform coordinates the operational lifecycle across four primary application clients and a central backend service:
1. **Customer Android App:** Self-service service discovery, upfront price estimations, slot selection, digital payments, real-time appointment tracking, AMC renewals, and service history.
2. **Technician Android App:** Offline-capable field execution, job queue management, route navigation, task checklists, chemical dosage recording, photo evidence capture, and on-site customer signature acquisition.
3. **Admin Web ERP Dashboard:** Centralized operations management, multi-branch dispatch boards, capacity management, billing reconciliation, technician skills matrix, inventory controls, and financial reporting.
4. **Backend REST API:** Authoritative validation, business logic execution, state machine transitions, multi-tenant security isolation, and event coordination.

---

# 3. User Classes & Stakeholder Personas

| Stakeholder Persona | Description & Primary Objectives |
|:---|:---|
| **Customer** | End-consumer or corporate facility manager ordering pest control treatments, scheduling appointments, and managing invoices. |
| **Field Technician** | Field operative executing treatments on-site, recording chemical usage, and capturing customer sign-offs. |
| **Agency / Branch Manager** | Regional supervisor overseeing local field force allocation, branch chemical stock, and operational expenses. |
| **Dispatcher** | Operations specialist managing daily job queues, resolving scheduling conflicts, and balancing technician workloads. |
| **Accountant** | Financial controller managing invoice generation, payment reconciliations, branch profit & loss, and tax reporting. |
| **Super Admin** | System administrator configuring global service catalogs, pricing rules, branch territories, and user permissions. |

---

# 4. Role-Based Access Control (RBAC) Requirements

The platform shall enforce strict role-based access control across all APIs and user interfaces:

| Capability / Resource Area | Customer | Field Technician | Agency Manager | Dispatcher | Accountant | Super Admin |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Browse Public Service Catalog & Rates | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Create Self-Service Booking | ✅ | ❌ | ❌ | ✅ (Manual) | ❌ | ✅ (Manual) |
| View Own Assigned Tasks / Bookings | ✅ (Own) | ✅ (Assigned) | ✅ (Branch) | ✅ (All) | ✅ (All) | ✅ (All) |
| Accept / Reject Assigned Work Orders | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Execute Service Visit & Log Chemicals | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ (Override) |
| Manual Dispatch & Assignment | ❌ | ❌ | ✅ (Branch) | ✅ | ❌ | ✅ |
| Manage Service Catalog & Dynamic Prices | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Manage Branch Chemical Stock & Restock | ❌ | ❌ | ✅ (Branch) | ❌ | ❌ | ✅ |
| Log Operating Expenses | ❌ | ❌ | ✅ (Branch) | ❌ | ✅ | ✅ |
| Access Financial Reports & P&L Statements | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Access System Audit Logs | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

# 5. 3-Tier Operational Domain Concept

To support multi-visit treatments, warranty follow-ups, and recurring AMC contracts without duplicating commercial records, the platform shall enforce a 3-tier operational separation:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        1. Commercial Request                            │
│                              BOOKING                                    │
│  • Customer Details, Target Address, Selected Services, Pricing Model  │
│  • Commercial Status: PENDING, CONFIRMED, IN_PROGRESS, COMPLETED, CLOSED│
│  • Payment Settlement Status: PENDING, AUTHORIZED, PAID, PARTIAL, etc. │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ 1 : N
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       2. Operational Assignment                         │
│                             WORK ORDER                                  │
│  • Operational Scope (Initial Treatment, Warranty Follow-Up, AMC Run)  │
│  • Assigned Agency, Territory, Priority, SLA Due Date                   │
│  • Operational Status: UNASSIGNED, ASSIGNED, IN_PROGRESS, COMPLETED     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ 1 : N
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        3. Physical Execution                            │
│                            SERVICE VISIT                                │
│  • Assigned Field Technician, Scheduled Date & Time Slot                │
│  • Visit Status: SCHEDULED, ON_THE_WAY, ARRIVED, STARTED, COMPLETED     │
│  • Field Evidence: Timestamps, Checklist, Chemicals Used, Photos, Sign │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# 6. Functional Requirements

## 6.1 Authentication & User Management
* **REQ-AUTH-001:** The platform shall authenticate Customers using Mobile Phone Number with SMS One-Time Password (OTP), with optional Google Sign-In federation.
* **REQ-AUTH-002:** The platform shall authenticate Field Technicians using Employee ID/Mobile Number and a secure PIN paired with registered device hardware.
* **REQ-AUTH-003:** The platform shall authenticate Administrative and Operational users using Corporate Email and Password enforced by Multi-Factor Authentication (MFA).
* **REQ-AUTH-004:** The platform shall validate all user identity tokens on every API request and immediately reject deactivated accounts regardless of token validity.

## 6.2 Customer & Address Management
* **REQ-CUST-001:** The platform shall allow Customers to maintain multiple service addresses with structured street address, city, postal code, and geographic coordinates (latitude/longitude).
* **REQ-CUST-002:** The platform shall maintain customer profiles, corporate GST numbers for commercial clients, communication preferences, and complete service histories.

## 6.3 Service Catalog & Pricing Engine
* **REQ-CAT-001:** The platform shall support a hierarchical service catalog organized by categories, service definitions, treatment packages, and warranty terms.
* **REQ-CAT-002:** The platform shall compute service pricing dynamically on the server based on configurable pricing models (unit area, BHK configuration, property type, pest severity level, and add-on treatments).
* **REQ-CAT-003:** The platform shall support promotional coupon validation with constraints for date validity, minimum order value, customer usage limits, and maximum discount caps.

## 6.4 Commercial Bookings & Slot Reservations
* **REQ-BKG-001:** The platform shall allow Customers and Dispatchers to create commercial bookings selecting services, service address, preferred date, and time slot.
* **REQ-BKG-002:** The platform shall maintain availability slot capacity per agency territory and prevent overbooking by reserving slot capacity upon booking initiation.
* **REQ-BKG-003:** For Cash on Delivery (COD) bookings, the platform shall confirm the booking upon slot reservation while keeping payment status as `PENDING`.
* **REQ-BKG-004:** For Prepaid bookings, the platform shall confirm the booking only after server verification of successful payment authorization.
* **REQ-BKG-005:** The platform shall support booking rescheduling and cancellation with automated slot capacity adjustments.

## 6.5 Dispatch, Work Orders & Field Scheduling
* **REQ-DSP-001:** The platform shall automatically generate an operational Work Order upon booking confirmation.
* **REQ-DSP-002:** The platform shall provide a visual dispatch board for Dispatchers and Agency Managers displaying technician workloads, open work orders, and geographic routes.
* **REQ-DSP-003:** The platform shall enforce skill matching, preventing technician assignment if the technician lacks required certifications for the service.
* **REQ-DSP-004:** The platform shall allow technicians to accept or reject assigned jobs within a configurable SLA window; rejected jobs shall return to the unassigned pool for redispatch.

## 6.6 Field Operations & Offline Mobile Execution
* **REQ-FLD-001:** The platform shall support full offline mobile execution for Field Technicians in zero-connectivity environments, storing actions locally and synchronizing when connectivity resumes.
* **REQ-FLD-002:** The platform shall track field visit state transitions: `SCHEDULED` $\rightarrow$ `ON_THE_WAY` $\rightarrow$ `ARRIVED` $\rightarrow$ `STARTED` $\rightarrow$ `COMPLETED` (or `FAILED`).
* **REQ-FLD-003:** The mobile application shall capture mandatory service evidence: GPS arrival coordinates, pre-treatment photos, dynamic task checklist verification, post-treatment photos, chemical batch usage, and customer digital signature.
* **REQ-FLD-004:** The platform shall resolve offline synchronization conflicts deterministically, preserving completed field work and logging audit entries for concurrent modifications.

## 6.7 Payments, Cash Collection & Invoicing
* **REQ-PAY-001:** The platform shall integrate with trusted payment gateways to support card, net banking, and UPI transactions without trusting client-declared payment success.
* **REQ-PAY-002:** The platform shall process payment gateway webhooks idempotently using provider event identifiers and validate payment state transitions.
* **REQ-PAY-003:** The platform shall support Cash on Delivery (COD) collection by field technicians with daily branch cash handover reconciliation workflows.
* **REQ-PAY-004:** The platform shall generate immutable sequential PDF invoices (`INV-YYYY-NNNNN`) upon payment completion or service completion, uploading them to secure object storage and delivering them to the customer.
* **REQ-PAY-005:** The platform shall maintain an authoritative payment lifecycle: `PENDING`, `AUTHORIZED`, `PAID`, `PARTIAL`, `FAILED`, `REFUNDED`, `PARTIALLY_REFUNDED`.

## 6.8 Inventory & Chemical Management
* **REQ-INV-001:** The platform shall track chemical products, regulatory pesticide registration numbers, and batch expiration dates enforcing First-In, First-Out (FIFO) consumption.
* **REQ-INV-002:** The platform shall track inventory across multiple physical tiers: Central Warehouse $\rightarrow$ Branch Warehouse $\rightarrow$ Technician Trunk Stock $\rightarrow$ Service Consumption.
* **REQ-INV-003:** The platform shall execute authoritative inventory deductions within the service visit completion transaction and reject deductions exceeding available batch quantities.
* **REQ-INV-004:** The platform shall calculate the exact material Cost of Goods Sold (COGS) for every completed service visit based on batch unit costs.

## 6.9 Branch Expense & Operational Accounting
* **REQ-EXP-001:** The platform shall allow Agency Managers to record branch operational expenses (fuel, vehicle maintenance, safety equipment, local overhead) with receipt image attachments.
* **REQ-EXP-002:** The platform shall provide gross margin and net operating profit calculations per branch, technician, and service category.

## 6.10 Annual Maintenance Contracts (AMC)
* **REQ-AMC-001:** The platform shall support multi-visit Annual Maintenance Contracts (Quarterly, Bi-Monthly, Monthly) with contract term tracking.
* **REQ-AMC-002:** The platform shall automatically generate child operational work orders for upcoming AMC visits 7 days prior to their scheduled due date.

## 6.11 Customer Support, Ratings & Escalations
* **REQ-SUP-001:** The platform shall capture 1-to-5 star customer ratings and written feedback following service completion.
* **REQ-SUP-002:** The platform shall automatically generate high-priority support escalation tickets for any service rated below 3 stars.
* **REQ-SUP-003:** The platform shall support warranty revisit claims linked to original booking records.

## 6.12 Notifications & Alerts Engine
* **REQ-NOT-001:** The platform shall deliver real-time push notifications, transactional SMS messages, and formatted email receipts for critical operational events (booking confirmation, technician arrival, service completion, payment receipt).

## 6.13 Audit Trails & Compliance
* **REQ-AUD-001:** The platform shall record an immutable, append-only audit trail for all business state transitions, administrative modifications, inventory adjustments, and dispatch overrides.

## 6.14 Executive Reporting & Analytics
* **REQ-REP-001:** The platform shall provide executive dashboards with operational and financial KPIs: revenue, job completion rate, technician utilization, customer retention, and regional profitability.
* **REQ-REP-002:** The platform shall provide paginated, filterable tabular reporting with asynchronous CSV and Excel export capabilities.

---

# 7. Non-Functional Requirements (NFR)

### 7.1 Performance & Latency
* **NFR-PERF-001:** The backend API shall respond within 250 ms for 95% of standard read and write requests under normal operational load.
* **NFR-PERF-002:** Service catalog and pricing rule lookups shall be optimized to support responsive mobile browsing.

### 7.2 Security & Data Protection
* **NFR-SEC-001:** All client-server communications shall use TLS 1.3 encryption.
* **NFR-SEC-002:** The platform shall enforce strict multi-tenant agency data isolation preventing cross-branch resource access.
* **NFR-SEC-003:** No Personally Identifiable Information (PII), authentication tokens, or raw payment card data shall ever be recorded in system logs.

### 7.3 Reliability & Availability
* **NFR-REL-001:** The platform shall maintain a 99.9% service availability SLA during operational business hours.
* **NFR-REL-002:** Asynchronous domain event publication shall guarantee at-least-once delivery using a transactional outbox mechanism.

### 7.4 Offline Durability & Data Integrity
* **NFR-DATA-001:** The Technician Mobile Application shall ensure zero data loss for on-site execution evidence when operating without network connectivity.
* **NFR-DATA-002:** All financial transactions, inventory balances, and booking state transitions shall maintain 100% ACID consistency.

---

# 8. Phased Release Scope

| Functional Area / Capability | Release 1 (Core Operations) | Release 2 (Financial & ERP) | Release 3 (Advanced Automation) |
|:---|:---:|:---:|:---:|
| Customer App: Authentication, Catalog, Booking | ✅ | — | — |
| Technician App: Offline Room Queue, Checklists | ✅ | — | — |
| Admin Web ERP: Core Dispatch & Booking Board | ✅ | — | — |
| Push Notifications (FCM Alerts) | ✅ | — | — |
| Online Payment Gateways (Razorpay/Stripe) & COD | — | ✅ | — |
| Sequential PDF Invoicing Engine | — | ✅ | — |
| Multi-Tier Inventory, Batch FIFO & COGS | — | ✅ | — |
| Branch Expenses & P&L Reporting | — | ✅ | — |
| Photo Evidence Capture & Digital Signatures | — | ✅ | — |
| Support Ticketing & Low-Rating Escalations | — | ✅ | — |
| AMC Contract Automation & Scheduled Visits | — | — | ✅ |
| Intelligent Automated Technician Dispatching | — | — | ✅ |
| Agency Multi-Tenant Management Portal | — | — | ✅ |
| WhatsApp Business Channel Integration | — | — | ✅ |
| Mobile Barcode Scanning for Chemical Batches | — | — | ✅ |
