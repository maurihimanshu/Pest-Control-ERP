# Software Requirements Specification (SRS)
## Pest Control Enterprise Resource Planning (ERP) System

**Document Version:** 2.0.0  
**Backend Framework:** Java 21 + Spring Boot 3.3.x (Modular Monolith)  
**Primary Database:** PostgreSQL 16  
**Cache & Message Broker:** Redis 7.x & RabbitMQ 3.13.x  
**Target Systems:** Customer Android App, Technician Android App, Admin Web ERP Dashboard  
**Date:** September 2026  

---

## Table of Contents

1. [Executive Summary & Purpose](#1-executive-summary--purpose)
2. [Overall System Architecture & Tech Stack](#2-overall-system-architecture--tech-stack)
3. [User Roles & RBAC Permission Matrix](#3-user-roles--rbac-permission-matrix)
4. [3-Tier Operational Domain Model](#4-3-tier-operational-domain-model)
5. [Functional Requirements (Module-by-Module)](#5-functional-requirements-module-by-module)
   - [5.1 Authentication & Profile Management](#51-authentication--profile-management)
   - [5.2 Service Catalog & Dynamic Pricing Engine](#52-service-catalog--dynamic-pricing-engine)
   - [5.3 Booking & State Machine Engine](#53-booking--state-machine-engine)
   - [5.4 Field Technician Operations & Offline Sync](#54-field-technician-operations--offline-sync)
   - [5.5 Payment Gateway, Invoicing & Financial Transactions](#55-payment-gateway-invoicing--financial-transactions)
   - [5.6 Admin Operations, Dispatching & Resource Management](#56-admin-operations-dispatching--resource-management)
   - [5.7 Agency / Branch Management](#57-agency--branch-management)
   - [5.8 Inventory & Chemical Management](#58-inventory--chemical-management)
   - [5.9 Expense & Revenue Management](#59-expense--revenue-management)
   - [5.10 AMC (Annual Maintenance Contracts) & Recurring Services](#510-amc-annual-maintenance-contracts--recurring-services)
   - [5.11 Feedback, Ratings & Support Ticketing](#511-feedback-ratings--support-ticketing)
   - [5.12 Notification & Communications Engine](#512-notification--communications-engine)
   - [5.13 Audit Logging & Compliance](#513-audit-logging--compliance)
6. [Requirements Traceability Matrix](#6-requirements-traceability-matrix)
7. [Non-Functional Requirements (NFR)](#7-non-functional-requirements-nfr)
8. [Phased Release Scope (Release 1, 2 & 3)](#8-phased-release-scope-release-1-2--3)

---

# 1. Executive Summary & Purpose

The **Pest Control ERP Platform** is a unified, multi-platform software suite engineered to digitize and automate the entire operational lifecycle of a modern pest control enterprise.

The platform coordinates interactions among four primary stakeholder groups:
1. **Customers:** Discover pest control services, request quotes, schedule visits, make payments, track technician status, and access service histories.
2. **Technicians (Field Force):** Receive job assignments, navigate to client sites, execute treatment protocols offline/online, capture evidence (before/after photos), record chemical usage, and obtain customer sign-offs.
3. **Agency/Branch Managers:** Monitor local technicians, manage branch inventory, and track regional revenue/commissions.
4. **Central Administrators / Executives:** Control service catalogs, manage dynamic pricing, dispatch technicians, audit financial entries, reconcile accounts, and analyze operational KPIs.

---

# 2. Overall System Architecture & Tech Stack

```text
                         ┌──────────────────────────┐
                         │      React Admin Web     │
                         │   React 18 + TypeScript  │
                         └────────────┬─────────────┘
                                      │ HTTPS / REST
                         ┌────────────▼─────────────┐
                         │       REST API            │
                         │      Spring Boot          │
                         │        Java 21           │
                         └────────────┬─────────────┘
                                      │
        ┌─────────────────────────────┼──────────────────────────────┐
        │                             │                              │
        ▼                             ▼                              ▼
 Customer Android              Technician Android              Admin Web
 Java 21                       Java 21                         React/TS
 Firebase Auth                 Firebase Auth                   Firebase Auth
 REST API                      REST API                        REST API
 Room Database                 Room Database                   State Store
 WorkManager                   WorkManager                     Ant Design
 CameraX                       CameraX                         Recharts
        │                             │                              │
        └─────────────────────────────┼──────────────────────────────┘
                                      │
                             ┌────────▼─────────┐
                             │   Spring Boot    │
                             │ Modular Monolith │
                             └────────┬─────────┘
                                      │
                    ┌─────────────────┼──────────────────┐
                    ▼                 ▼                  ▼
               PostgreSQL          Redis             RabbitMQ
               Primary DB          Cache             Async Events
                    │
                    ▼
              Object Storage
          Photos / Documents / PDFs
```

### Technology Matrix:
* **Backend:** Java 21 LTS, Spring Boot 3.3.x, Maven, Spring Security, Spring Data JPA, Hibernate, Flyway.
* **Primary Database:** PostgreSQL 16 (Authoritative System-of-Record).
* **Caching & Locking:** Redis 7.2 (Distributed Redlock for slot bookings & catalog caching).
* **Asynchronous Events:** RabbitMQ 3.13 (Decoupled event handling for notifications, invoicing, and inventory).
* **Identity Provider:** Firebase Authentication (Client OTP / PIN verification $\rightarrow$ Spring Boot token filter).
* **Push Alerts:** Firebase Cloud Messaging (FCM HTTP v1 API).
* **Object Storage:** Provider-neutral S3-compatible storage for photos, PDFs, and attachments.

---

# 3. User Roles & RBAC Permission Matrix

System access is enforced via **Spring Security** validating incoming Firebase JWT tokens and querying PostgreSQL user roles.

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

# 4. 3-Tier Operational Domain Model

To support multi-visit jobs, recurring AMC contracts, and warranty visits without data duplication, the business model separates commercial, operational, and execution concerns:

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
│  • Field Evidence (Chemicals Used, Batch Nos, Photos, Signature)       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# 5. Functional Requirements (Module-by-Module)

## 5.1 Authentication & Profile Management
* **Customer App:** Mobile Phone Number + SMS OTP (Primary) with Google Sign-In fallback.
* **Technician App:** Employee ID / Mobile + Secure PIN paired with device UUID.
* **Admin Web Dashboard:** Corporate Email + Password enforced with Multi-Factor Authentication (MFA).
* **Token Verification:** Spring Boot `FirebaseAuthenticationFilter` validates ID tokens and resolves user records from PostgreSQL.

## 5.2 Service Catalog & Dynamic Pricing Engine
* **Hierarchical Structure:** Categories $\rightarrow$ Services $\rightarrow$ Pricing Rules.
* **Dynamic Pricing Engine:** Handled server-side in `PricingService`:
  $$\text{Base Amount} = \text{Unit Price} \times \text{Quantity / Area}$$
  $$\text{Subtotal} = \text{Base Amount} + \sum \text{Add-ons}$$
  $$\text{Discounted Subtotal} = \max(0, \text{Subtotal} - \text{Coupon Discount})$$
  $$\text{Total Payable} = \text{Discounted Subtotal} + \text{Taxes}$$

## 5.3 Booking & State Machine Engine
* Separate state machines for **Booking Status**, **Work Order Status**, and **Service Visit Status**.
* Concurrency protection via **Redis distributed locks** preventing slot double-booking.

## 5.4 Field Technician Operations & Offline Sync
* **Offline-First Field Execution:** SQLite (Room DB) action queue with cryptographic monotonic sequencing.
* **CameraX Media Capture:** Local WebP compression ($<500\text{ KB}$) before upload.
* **Background Sync:** Android `WorkManager` pushes queued actions to `POST /api/v1/dispatch/visits/sync`.
* **Deterministic Conflict Resolution:** Field physical completion overrides concurrent online cancellations with audit logging.

## 5.5 Payment Gateway, Invoicing & Financial Transactions
* Tokenized payment initiation via `POST /api/v1/payments/initiate`.
* HMAC-SHA256 signature verification on gateway webhooks.
* Cash on Delivery (COD) field collection and daily branch cash reconciliation.
* Automated sequential PDF invoice generation (`INV-2026-00001`) via Spring Boot PDF builder.

## 5.6 Admin Operations, Dispatching & Resource Management
* Visual Gantt and calendar dispatch boards with technician skill matching.
* Real-time technician workload balancing.

## 5.7 Agency / Branch Management
* Regional branch data isolation by postal/pincode boundary.
* Agency commission tracking and settlement reports.

## 5.8 Inventory & Chemical Management
* Chemical product registration and batch tracking with expiration dates (FIFO).
* Multi-tier tracking: Central Warehouse $\rightarrow$ Branch Warehouse $\rightarrow$ Technician Trunk Stock $\rightarrow$ Service Visit Consumption.
* Automated material Cost of Goods Sold (COGS) calculation per job.

## 5.9 Expense & Revenue Management
* Branch operating expense logging with receipt file attachments.
* Profit & Loss calculation:
  $$\text{Net Margin} = \text{Gross Revenue} - (\text{Chemical COGS} + \text{Commissions} + \text{Operating Expenses})$$

## 5.10 AMC (Annual Maintenance Contracts) & Recurring Services
* Multi-visit contract structures (Quarterly, Bi-Monthly, Monthly).
* Spring Scheduler cron job running daily to auto-generate child work orders 7 days prior to visit due date.

## 5.11 Feedback, Ratings & Support Ticketing
* Post-service ratings (1–5 Stars); ratings $<3$ stars auto-generate high-priority support tickets for manager escalation.

## 5.12 Notification & Communications Engine
* RabbitMQ event listeners dispatching alerts across FCM Push, Transactional SMS (MSG91/Twilio), and HTML Emails (Thymeleaf).

## 5.13 Audit Logging & Compliance
* Immutable, append-only PostgreSQL `audit_logs` capturing actor, action, entity, before/after JSON values, and IP addresses.

---

# 6. Requirements Traceability Matrix

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

# 7. Non-Functional Requirements (NFR)

| Parameter | Target SLA | Implementation Architecture |
| :--- | :--- | :--- |
| **API Response Latency** | $< 250\text{ ms}$ for 95% of requests | PostgreSQL composite B-tree indexes & Redis caching for catalog/pricing. |
| **Field Offline Durability**| Zero data loss in zero-signal zones | Encrypted SQLite Room queue with WorkManager exponential backoff. |
| **Data Integrity** | 100% ACID compliance for billing | PostgreSQL transactions (`@Transactional`), foreign keys, and idempotency keys. |
| **High Availability** | 99.9% uptime | Containerized Spring Boot instances behind Nginx load balancing. |

---

# 8. Phased Release Scope (Release 1, 2 & 3)

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
