# Software Requirements Specification (SRS)
## Pest Control Enterprise Resource Planning (ERP) System

**Document Version:** 2.1.0  
**Backend Framework:** Java 21 + Spring Boot 3.3.x (Maven Modular Monolith)  
**Primary Database:** PostgreSQL 16  
**Cache & Message Broker:** Redis 7.2 & RabbitMQ 3.13  
**Target Systems:** Customer Android App, Technician Android App, Admin Web ERP Dashboard, Spring Boot REST Backend  
**Supporting Services:** Firebase Authentication, Firebase Cloud Messaging, Provider-Neutral Object Storage  
**Date:** September 2026  

---

## Table of Contents

1. [Executive Summary & Purpose](#1-executive-summary--purpose)
2. [Overall System Architecture](#2-overall-system-architecture)
3. [Spring Boot Modular Monolith Architecture](#3-spring-boot-modular-monolith-architecture)
4. [User Roles & RBAC Permission Matrix](#4-user-roles--rbac-permission-matrix)
5. [3-Tier Operational Domain Model](#5-3-tier-operational-domain-model)
6. [PostgreSQL Relational Data Model](#6-postgresql-relational-data-model)
7. [Spring Boot REST API & State Machine Specifications](#7-spring-boot-rest-api--state-machine-specifications)
8. [Functional Requirements (Module Breakdown)](#8-functional-requirements-module-breakdown)
   - [8.1 Authentication & Profile Management](#81-authentication--profile-management)
   - [8.2 Service Catalog & Dynamic Pricing Engine](#82-service-catalog--dynamic-pricing-engine)
   - [8.3 Booking & State Machine Engine](#83-booking--state-machine-engine)
   - [8.4 Field Technician Operations & Offline Sync](#84-field-technician-operations--offline-sync)
   - [8.5 Payment Gateway, Invoicing & Financial Transactions](#85-payment-gateway-invoicing--financial-transactions)
   - [8.6 Admin Operations, Dispatching & Resource Management](#86-admin-operations-dispatching--resource-management)
   - [8.7 Agency / Branch Management](#87-agency--branch-management)
   - [8.8 Inventory & Chemical Management](#88-inventory--chemical-management)
   - [8.9 Expense & Revenue Management](#89-expense--revenue-management)
   - [8.10 AMC (Annual Maintenance Contracts) & Recurring Services](#810-amc-annual-maintenance-contracts--recurring-services)
   - [8.11 Feedback, Ratings & Support Ticketing](#811-feedback-ratings--support-ticketing)
   - [8.12 Notification & Communications Engine](#812-notification--communications-engine)
   - [8.13 Audit Logging & Compliance](#813-audit-logging--compliance)
9. [Requirements Traceability Matrix](#9-requirements-traceability-matrix)
10. [Non-Functional Requirements (NFR)](#10-non-functional-requirements-nfr)
11. [Phased Release Scope (Release 1, 2 & 3)](#11-phased-release-scope-release-1-2--3)

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
 ┌────────────────────────┐             ┌────────────────────────┐             ┌────────────────────────┐
 │  Customer Android App  │             │ Technician Android App │             │    Admin Web ERP App   │
 │   (Native Java 21)     │             │(Java 21, Offline Room) │             │ (React 18 + TypeScript)│
 └───────────┬────────────┘             └───────────┬────────────┘             └───────────┬────────────┘
             │                                      │                                      │
             └──────────────────────────────────────┼──────────────────────────────────────┘
                                                    │ HTTPS / REST (JSON)
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │       Spring Boot REST API Layer        │
                               │          (Java 21 / Maven 3.x)          │
                               └────────────────────┬────────────────────┘
                                                    │
                               ┌────────────────────▼────────────────────┐
                               │    Spring Boot Modular Monolith Core    │
                               │                                         │
                               │ • Spring Security & Firebase JWT Filter │
                               │ • Domain Services & Business Rules      │
                               │ • Spring Data JPA / Hibernate Layer     │
                               │ • RabbitMQ Event Publishers & Consumers │
                               │ • Spring Scheduler & Redis Redlock      │
                               └───────┬────────────┬────────────┬───────┘
                                       │            │            │
                      ┌────────────────┴────┐  ┌────┴──────┐ ┌───┴──────────────────┐
                      ▼                     ▼  ▼           ▼ ▼                      ▼
             ┌──────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌───────────────────┐
             │    PostgreSQL    │ │     Redis      │ │    RabbitMQ    │ │  Object Storage   │
             │ Primary Database │ │ Cache & Locks  │ │  Async Events  │ │ (S3/Cloud Storage)│
             │(System-of-Record)│ └────────────────┘ └────────────────┘ └───────────────────┘
             └──────────────────┘
                                             │
                                             ▼
             ┌──────────────────────────────────────────────────────────────────────────────┐
             │                         External Supporting Services                         │
             │ • Firebase Authentication (Identity Provider for Customer, Tech & Admin)     │
             │ • Firebase Cloud Messaging (FCM HTTP v1 Push Alerts)                         │
             │ • Payment Gateways (Razorpay / Stripe Webhook Integration)                   │
             │ • Google Maps Platform (Geocoding & Places Autocomplete)                     │
             │ • Transactional SMS / WhatsApp Provider (MSG91 / Twilio)                     │
             │ • Transactional Email Provider (SendGrid / Resend)                           │
             └──────────────────────────────────────────────────────────────────────────────┘
```

---

# 3. Spring Boot Modular Monolith Architecture

The backend is built as a single deployable **Modular Monolith** organized into 18 distinct domain modules:

```text
backend/src/main/java/com/pestcontrol/modules/
├── auth/          # Firebase ID token validation, custom claims, and session filters
├── users/         # User accounts, status, and role mappings
├── customers/     # Customer profiles, property addresses, and contact preferences
├── employees/     # Technician profiles, certifications, skills matrix, and shifts
├── agencies/      # Branches, franchises, regional territories, and commissions
├── services/      # Service catalog, categories, packages, and required skills
├── pricing/       # Dynamic pricing calculations, area/BHK rules, and coupon engine
├── bookings/      # Customer-facing commercial bookings and line items
├── scheduling/    # Calendar availability, slot reservations, and Redis locks
├── dispatch/      # Work orders, service visits, field assignment, and offline sync
├── payments/      # Payment gateway initiation, webhook verification, and COD
├── invoices/      # Sequential invoice numbering, PDF generation, and receipts
├── expenses/      # Branch operational expenses, fuel logs, and receipt files
├── inventory/     # Chemical products, batch FIFO expiry, and trunk stock allocation
├── amc/           # Annual Maintenance Contracts and automated visit generators
├── notifications/ # Event-driven multi-channel dispatch (FCM, SMS, Email, WhatsApp)
├── support/       # Customer complaints, warranty claims, and ticket escalation
├── reports/       # PostgreSQL reporting queries, daily KPI aggregations, and exports
└── audit/         # Append-only database audit logs for all administrative mutations
```

> **Architectural Guardrail:** The initial implementation is a modular monolith, not a distributed microservice system. Modules are isolated by domain boundaries and may be extracted into independent services later if justified by scale, ownership, deployment independence, or reliability requirements.

---

# 4. User Roles & RBAC Permission Matrix

Authorization is enforced via **Spring Security** evaluating user roles loaded from PostgreSQL upon validating the client's Firebase ID token.

| Capability / Module | Customer | Field Technician | Agency Manager | Dispatcher | Accountant | Super Admin |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Browse Services & Rates | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Create Self-Service Booking | ✅ | ❌ | ❌ | ✅ (Manual) | ❌ | ✅ (Manual) |
| View Own Bookings / Tasks | ✅ (Own) | ✅ (Assigned) | ✅ (Branch) | ✅ (All) | ✅ (All) | ✅ (All) |
| Accept / Reject Assigned Job | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Start Service & Log Chemicals | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ (Override) |
| Manual Dispatch & Assignment | ❌ | ❌ | ✅ (Branch) | ✅ | ❌ | ✅ |
| Manage Service Catalog & Prices| ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Chemical Inventory & Restock | ❌ | ❌ | ✅ (Branch) | ❌ | ❌ | ✅ |
| Log Operating Expenses | ❌ | ❌ | ✅ (Branch) | ❌ | ✅ | ✅ |
| View Executive Revenue & P&L | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| View System Audit Logs | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

# 5. 3-Tier Operational Domain Model

To support multi-visit jobs, recurring AMC contracts, and warranty visits without data duplication, the domain model separates commercial, operational, and execution concerns:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        1. Commercial Request                            │
│                              BOOKING                                    │
│  • Customer Details, Target Address, Selected Services, Pricing Model  │
│  • Commercial Status (PENDING, CONFIRMED, CANCELLED, CLOSED)            │
│  • Billing & Payment Status (PENDING, PAID, REFUNDED)                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ 1 : N
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       2. Operational Assignment                         │
│                             WORK ORDER                                  │
│  • Operational Scope (Initial Treatment, Warranty Follow-Up, AMC Run)  │
│  • Assigned Branch/Agency, Dispatch Priority, SLA Due Date             │
│  • Operational Status (UNASSIGNED, ASSIGNED, IN_PROGRESS, COMPLETED)   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ 1 : N
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        3. Physical Execution                            │
│                            SERVICE VISIT                                │
│  • Primary Field Technician, Scheduled Date & Time Slot                 │
│  • Visit Status (SCHEDULED, EN_ROUTE, ARRIVED, IN_PROGRESS, COMPLETED)  │
│  • Field Evidence: Arrival/Start/End Timestamps, Checklist Verification │
│    Chemicals Used & Batch Nos, Before/After Photos, Customer Signature  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# 6. PostgreSQL Relational Data Model

PostgreSQL 16 is the authoritative **System-of-Record (SoR)**. Foreign keys, constraints, and transactions govern all business entities:

```text
┌───────────────────────────┬─────────────────────────────────────────────────────────────────┐
│ Relational Entity         │ Key Fields & Foreign Key Relationships                          │
├───────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ `users`                   │ id (UUID), firebase_uid, email, phone_number, full_name, active │
│ `roles` & `user_roles`    │ id, description; many-to-many user-role assignments             │
│ `customers`               │ id, user_id (FK), customer_type, company_name, gst_number       │
│ `customer_addresses`      │ id, customer_id (FK), line1, city, state, pincode, lat, lng     │
│ `employees`               │ id, user_id (FK), agency_id (FK), employee_code, rating, active │
│ `skills` & `emp_skills`   │ skill_id, title; many-to-many employee certification matrix     │
│ `agencies`                │ id, agency_code, name, commission_rate, service_pincodes[]      │
│ `service_categories`      │ id, name, slug, display_order, is_active                        │
│ `services`                │ id, category_id (FK), title, pricing_model, base_price, warranty│
│ `pricing_rules` / `tiers` │ id, service_id (FK), tier_name, unit_min, unit_max, unit_price  │
│ `coupons`                 │ code (PK), discount_type, discount_value, min_amount, valid_to  │
│ `coupon_redemptions`      │ id, coupon_id (FK), customer_id (FK), booking_id (FK), redeemed_at  │
│ `bookings`                │ id, booking_number, customer_id (FK), address_id (FK), status   │
│ `booking_items`           │ id, booking_id (FK), service_id (FK), pricing_tier, line_total  │
│ `work_orders`             │ id, work_order_number, booking_id (FK), assigned_employee_id(FK)│
│ `service_visits`          │ id, visit_number, work_order_id (FK), primary_employee_id (FK)  │
│ `booking_events`          │ id, booking_id (FK), event_type, actor_id (FK), timestamp       │
│ `payments`                │ id, payment_number, booking_id (FK), method, amount, status     │
│ `payment_events`          │ id, payment_id (FK), provider, gateway_event_id UNIQUE, event_type, processing_status │
│ `payment_transactions`    │ id, payment_id (FK), gateway_txn_id, amount, status, payload_json│
│ `invoices`                │ id, invoice_number, booking_id (FK), customer_id (FK), pdf_path │
│ `expenses`                │ id, agency_id (FK), category, amount, expense_date, receipt_url │
│ `chemical_products`       │ id, product_name, registration_number, unit_of_measure, reorder │
│ `chemical_batches`        │ id, product_id (FK), batch_number, expiry_date, available_qty  │
│ `service_material_usage`  │ id, visit_id (FK), batch_id (FK), quantity_used, dosage_rate    │
│ `amc_contracts`           │ id, contract_number, customer_id (FK), service_id (FK), visits  │
│ `amc_schedules`           │ id, contract_id (FK), scheduled_date, sequence, work_order_id  │
│ `support_tickets`         │ id, customer_id (FK), booking_id (FK), subject, status, priority│
│ `support_messages`        │ id, ticket_id (FK), sender_id (FK), message_body, attachment_url│
│ `notifications`           │ id, user_id (FK), channel, title, body, status, sent_at         │
│ `file_metadata`           │ id, entity_type, entity_id, storage_provider, storage_path, size│
│ `audit_logs`              │ id (BIGSERIAL), actor_id (FK), action, entity_type, old/new json│
│ `outbox_events`           │ id, event_type, aggregate_type, aggregate_id, payload, publication_status │
│ `idempotency_keys`        │ key PK, user_id, request_path, response_status, response_body, expires_at│
│ `availability_slots`      │ id, service_date, start_time, end_time, employee_id, capacity, booked_count│
└───────────────────────────┴─────────────────────────────────────────────────────────────────┘

> **Note:** `work_orders → service_visits` is 1:N. A single Work Order may generate multiple Service Visits to support: initial failed visits, rescheduled visits, warranty follow-up visits, AMC recurring visits, and multi-technician visits.
```

---

# 7. Spring Boot REST API & State Machine Specifications

### 7.1 Backend Service Component Mapping

```text
┌──────────────────────────────┬─────────────────────────────┬───────────────────────────────────────────┐
│ Spring Boot Component        │ Primary REST Endpoints      │ Asynchronous Event Triggers / Queues      │
├──────────────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ `PricingService`             │ POST /api/v1/pricing/calc   │ — (Synchronous validation & calculation)  │
│ `BookingService`             │ POST /api/v1/bookings       │ Emits `booking.created`, `booking.confirm`│
│ `DispatchService`            │ POST .../work-orders/assign │ Emits `workorder.assigned` $\rightarrow$ FCM Push│
│ `TechnicianJobService`       │ POST .../visits/{id}/complete│ Emits `visit.completed` $\rightarrow$ Invoicing │
│ `PaymentService`             │ POST .../payments/webhooks  │ Emits `payment.success` $\rightarrow$ Ledger/PDF │
│ `InvoiceService`             │ GET /api/v1/invoices/{id}   │ Consumes `payment.success` $\rightarrow$ OpenPDF│
│ `InventoryService`           │ POST /api/v1/inventory/*    │ Consumes `visit.completed` $\rightarrow$ Deduct  │
│ `AMCService`                 │ POST /api/v1/amc/contracts  │ Daily Cron $\rightarrow$ Emits `amc.visit_due`   │
│ `FinancialReportingService`  │ GET /api/v1/reports/*       │ Nightly Cron $\rightarrow$ Rollup aggregation    │
└──────────────────────────────┴─────────────────────────────┴───────────────────────────────────────────┘
```

---

# 8. Functional Requirements (Module Breakdown)

## 8.1 Authentication & Profile Management
* **Customer App:** Mobile Phone Number + SMS OTP (Primary) with Google Sign-In fallback.
* **Technician App:** Employee ID / Mobile + Secure PIN paired with device UUID.
* **Admin Web Dashboard:** Corporate Email + Password enforced with Multi-Factor Authentication (MFA).
* **Token Verification:** Spring Boot `FirebaseAuthenticationFilter` validates ID tokens and resolves user records from PostgreSQL.

## 8.2 Service Catalog & Dynamic Pricing Engine
* **Hierarchical Structure:** Categories $\rightarrow$ Services $\rightarrow$ Pricing Rules.
* **Dynamic Pricing Engine:** Handled server-side in `PricingService`:
  $$\text{Base Amount} = \text{Unit Price} \times \text{Quantity / Area}$$
  $$\text{Subtotal} = \text{Base Amount} + \sum \text{Add-ons}$$
  $$\text{Discounted Subtotal} = \max(0, \text{Subtotal} - \text{Coupon Discount})$$
  $$\text{Total Payable} = \text{Discounted Subtotal} + \text{Taxes}$$

## 8.3 Booking & State Machine Engine
* Separate state machines for **Booking Status**, **Work Order Status**, and **Service Visit Status**.
* Concurrency protection via **Redis distributed locks** preventing slot double-booking.

### Booking Confirmation Payment Rules
* **COD / Deferred Payment Model:** Booking transitions from PENDING to CONFIRMED immediately after slot availability is validated and locked. Payment status remains PENDING — the service will proceed with COD collection at completion.
* **Prepaid Model:** Booking transitions to CONFIRMED only after the backend verifies successful payment authorization from the payment gateway. Client-declared payment success is never accepted.
* The `booking_type` field on the booking determines which confirmation flow applies.

## 8.4 Field Technician Operations & Offline Sync
* **Offline-First Field Execution:** SQLite (Room DB) action queue with deterministic operation_id (UUID) for idempotency, monotonic local_sequence for ordering, and device_id registration. Cryptographic payload signing is deferred to a future security hardening phase.
* **CameraX Media Capture:** Local WebP compression ($<500\text{ KB}$) before upload.
* **Background Sync:** Android `WorkManager` pushes queued actions to `POST /api/v1/dispatch/visits/sync`.
* **Deterministic Conflict Resolution:** Field physical completion overrides concurrent online cancellations with audit logging.

## 8.5 Payment Gateway, Invoicing & Financial Transactions
* Tokenized payment initiation via `POST /api/v1/payments/initiate`.
* HMAC-SHA256 signature verification on gateway webhooks.
* Cash on Delivery (COD) field collection and daily branch cash reconciliation.
* Automated sequential PDF invoice generation (`INV-2026-00001`) via Spring Boot PDF builder.

## 8.6 Admin Operations, Dispatching & Resource Management
* Visual Gantt and calendar dispatch boards with technician skill matching.
* Real-time technician workload balancing.

## 8.7 Agency / Branch Management
* Regional branch data isolation by postal/pincode boundary.
* Agency commission tracking and settlement reports.

## 8.8 Inventory & Chemical Management
* Chemical product registration and batch tracking with expiration dates (FIFO).
* Multi-tier tracking: Central Warehouse $\rightarrow$ Branch Warehouse $\rightarrow$ Technician Trunk Stock $\rightarrow$ Service Visit Consumption.
* Automated material Cost of Goods Sold (COGS) calculation per job.

## 8.9 Expense & Revenue Management
* Branch operating expense logging with receipt file attachments.
* Profit & Loss calculation:
  $$\text{Net Margin} = \text{Gross Revenue} - (\text{Chemical COGS} + \text{Commissions} + \text{Operating Expenses})$$

## 8.10 AMC (Annual Maintenance Contracts) & Recurring Services
* Multi-visit contract structures (Quarterly, Bi-Monthly, Monthly).
* Spring Scheduler cron job running daily to auto-generate child work orders 7 days prior to visit due date.

## 8.11 Feedback, Ratings & Support Ticketing
* Post-service ratings (1–5 Stars); ratings $<3$ stars auto-generate high-priority support tickets for manager escalation.

## 8.12 Notification & Communications Engine
* RabbitMQ event listeners dispatching alerts across FCM Push, Transactional SMS (MSG91/Twilio), and HTML Emails (Thymeleaf).

## 8.13 Audit Logging & Compliance
* Immutable, append-only PostgreSQL `audit_logs` capturing actor, action, entity, before/after JSON values, and IP addresses.

---

# 9. Requirements Traceability Matrix

```text
┌─────────────────────────┬──────────────────┬─────────────────┬───────────────────┬───────────────────────────┬────────────────────┐
│ Business Requirement    │ Client App       │ Backend Module  │ DB Entities       │ Core API Endpoint         │ Async Event        │
├─────────────────────────┼──────────────────┼─────────────────┼───────────────────┼───────────────────────────┼────────────────────┤
│ Customer Books Service  │ Customer Android │ bookings        │ bookings, items   │ POST /api/v1/bookings     │ booking.confirmed  │
│ Dispatcher Assigns Tech │ Admin Web ERP    │ dispatch        │ work_orders       │ POST .../work-orders/assign│ workorder.assigned │
│ Tech Completes Job      │ Technician App   │ dispatch        │ service_visits    │ POST .../visits/complete  │ visit.completed    │
│ Payment Captured        │ Gateway Webhook  │ payments        │ payments, invoices│ POST .../webhooks/{gw}    │ payment.success    │
│ Chemical Logged         │ Technician App   │ inventory       │ service_material  │ POST .../visits/complete  │ inventory.deducted │
│ AMC Visit Due           │ Spring Scheduler │ amc             │ amc_schedules     │ (Internal Cron Task)      │ amc.visit_generated│
└─────────────────────────┴──────────────────┴─────────────────┴───────────────────┴───────────────────────────┴────────────────────┘
```

---

# 10. Non-Functional Requirements (NFR)

| Parameter | Target SLA | Implementation Architecture |
| :--- | :--- | :--- |
| **API Response Latency** | $< 250\text{ ms}$ for 95% of requests | PostgreSQL composite B-tree indexes & Redis caching for catalog/pricing. |
| **Field Offline Durability**| Zero data loss in zero-signal zones | Encrypted SQLite Room queue with WorkManager exponential backoff. |
| **Data Integrity** | 100% ACID compliance for billing | PostgreSQL transactions (`@Transactional`), foreign keys, and idempotency keys. |
| **High Availability** | 99.9% uptime | Containerized Spring Boot instances behind Nginx load balancing. |

---

# 11. Phased Release Scope (Release 1, 2 & 3)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              Phased Scope Matrix                                       │
├────────────────────────────────────────────┬─────────────┬─────────────┬───────────────┤
│ Capability / Module                        │ Release 1   │ Release 2   │ Release 3     │
│                                            │ (Core Ops)  │ (Fin & ERP) │ (Automation)  │
├────────────────────────────────────────────┼─────────────┼─────────────┼───────────────┤
│ Customer App (Auth, Catalog, Booking)      │     ✅      │      -      │       -       │
│ Technician App (Job queue, Checklist)      │     ✅      │      -      │       -       │
│ Technician Offline Room Cache              │     ✅      │      -      │       -       │
│ Admin Web ERP (Bookings, Tech Management)  │     ✅      │      -      │       -       │
│ Manual Dispatch Board                      │     ✅      │      -      │       -       │
│ Push Notifications (FCM)                   │     ✅      │      -      │       -       │
├────────────────────────────────────────────┼─────────────┼─────────────┼───────────────┤
│ Payment Gateway (Razorpay/Stripe) + COD    │      -      │     ✅      │       -       │
│ Automated PDF Invoicing Engine             │      -      │     ✅      │       -       │
│ Chemical Batch & Trunk Stock Tracking      │      -      │     ✅      │       -       │
│ Branch Expense & Profitability Dashboard   │      -      │     ✅      │       -       │
│ Customer Digital Signature & Photos        │      -      │     ✅      │       -       │
│ Support Ticketing & Low-Rating Escalation  │      -      │     ✅      │       -       │
├────────────────────────────────────────────┼─────────────┼─────────────┼───────────────┤
│ AMC Contract & Automated Recurring Visits  │      -      │      -      │      ✅       │
│ Intelligent AI Technician Dispatching      │      -      │      -      │      ✅       │
│ Agency / Branch Multi-Tenant Portal        │      -      │      -      │      ✅       │
│ Customer WhatsApp Business Integration     │      -      │      -      │      ✅       │
│ Advanced Inventory Barcode Scanning        │      -      │      -      │      ✅       │
└────────────────────────────────────────────┴─────────────┴─────────────┴───────────────┘
```

---

*This document defines the baseline functional and architectural requirements for implementation.*
