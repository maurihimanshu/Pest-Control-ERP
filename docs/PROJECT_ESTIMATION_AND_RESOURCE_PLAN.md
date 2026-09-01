# Pest Control ERP — Project Estimation, Resource Plan & Timeline

**Document Version:** 1.0.0  
**Target Project:** Pest Control Enterprise Resource Planning (ERP) System  
**Deliverables:** Customer Android App, Technician Android App, Web Admin ERP Dashboard, Firebase Cloud Backend  
**Date:** September 2026  

---

## Table of Contents

1. [Executive Summary & Estimation Methodology](#1-executive-summary--estimation-methodology)
2. [Work Breakdown Structure (WBS) & Effort Estimation](#2-work-breakdown-structure-wbs--effort-estimation)
   - [2.1 Backend, Database & Cloud Functions](#21-backend-database--cloud-functions)
   - [2.2 Customer Android Application](#22-customer-android-application)
   - [2.3 Technician Android Application (Offline-First)](#23-technician-android-application-offline-first)
   - [2.4 Web Admin ERP Dashboard](#24-web-admin-erp-dashboard)
   - [2.5 Quality Assurance, Security & Deployment](#25-quality-assurance-security--deployment)
3. [Required Manpower, Team Size & Skill Sets](#3-required-manpower-team-size--skill-sets)
4. [Project Timeline, Milestones & Sprint Schedule](#4-project-timeline-milestones--sprint-schedule)
5. [Comprehensive Cost Estimation](#5-comprehensive-cost-estimation)
   - [5.1 Engineering Manpower Cost Breakdown](#51-engineering-manpower-cost-breakdown)
   - [5.2 Cloud Infrastructure & Third-Party Recurring Costs](#52-cloud-infrastructure--third-party-recurring-costs)
   - [5.3 Total Cost of Ownership (TCO) Summary](#53-total-cost-of-ownership-tco-summary)
6. [Assumptions, Risks & Contingency Plan](#6-assumptions-risks--contingency-plan)

---

# 1. Executive Summary & Estimation Methodology

This document outlines the **resource allocation, manpower skill requirements, development effort, timeline, and cost estimates** for building the **Pest Control ERP System (MVP Release)** and preparing the foundation for future extensions.

### Methodology Used:
* **Effort Estimation:** Agile Story Points mapped to standard Engineering Hours using Work Breakdown Structure (WBS) based on the approved SRS.
* **Team Structure:** Cross-functional Agile squad operating in 2-week sprints.
* **Sprint Duration:** 8 Sprints (16 Weeks / ~4 Calendar Months) for MVP delivery.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Project Metric Summary                                 │
├──────────────────────────────────────┬─────────────────────────────────────────────────┤
│ Total Estimated Engineering Effort   │ 1,920 Hours (~240 Man-Days)                     │
│ Core Team Size                       │ 6 Full-Time Professionals + 2 Part-Time / Lead  │
│ MVP Delivery Timeline                │ 16 Weeks (4 Months)                             │
│ Estimated Development Cost (MVP)     │ $00,000 – $00,000 (INR ₹00.0L – ₹00.0L approx.) │
│ Estimated Monthly Cloud/SaaS Run Cost│ $000 – $000 / month (Variable based on volume)  │
└──────────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

# 2. Work Breakdown Structure (WBS) & Effort Estimation

Effort is broken down across the 5 primary pillars of the system for MVP delivery.

### 2.1 Backend, Database & Cloud Functions

| Task / Module | Complexity | Dev Hours |
| :--- | :---: | :---: |
| Firebase Architecture, Firestore Schema & Custom Claims Auth Setup | Medium | 32 hrs |
| Dynamic Pricing Calculation & Coupon Engine (`calculateCartPricing`) | High | 48 hrs |
| Booking State Machine & Transactional Locking Cloud Functions | High | 60 hrs |
| Payment Gateway Webhook Handling & Idempotency Engine | High | 40 hrs |
| Automated PDF Invoice Generator (`generateInvoicePdfOnComplete`) | Medium | 36 hrs |
| FCM Push Notification Dispatcher & Transactional SMS Engine | Medium | 32 hrs |
| Firestore Security Rules (RBAC) & Custom Claims Middleware | High | 40 hrs |
| Daily Financial Rollup & Aggregation Cloud Schedulers | Medium | 32 hrs |
| **Subtotal (Backend & Cloud)** | | **320 Hours** |

---

### 2.2 Customer Android Application (Java 21)

| Task / Module | Complexity | Dev Hours |
| :--- | :---: | :---: |
| App Scaffolding, Navigation, DI (Hilt/Dagger), Theme & Shared Components | Medium | 36 hrs |
| Phone Number OTP + Google Sign-In Authentication & Profile Setup | Medium | 40 hrs |
| Multi-Address Management with Google Maps Geocoding & Pin Placement | Medium | 36 hrs |
| Service Catalog, Hierarchical Browser & Category Filtering | Low | 28 hrs |
| Slot Picker, Dynamic Rate Summary & Checkout Flow | High | 54 hrs |
| Payment Gateway SDK Integration (UPI, Cards, Netbanking) & COD | High | 44 hrs |
| Live Booking Tracking Timeline & Push Notification Handler | Medium | 36 hrs |
| Service History, Invoice PDF Download & Review/Rating System | Medium | 36 hrs |
| In-App Customer Support Ticket Submission | Low | 24 hrs |
| **Subtotal (Customer App)** | | **334 Hours** |

---

### 2.3 Technician Android Application (Offline-First, Java 21)

| Task / Module | Complexity | Dev Hours |
| :--- | :---: | :---: |
| App Setup, Secure Device Binding, PIN Login & Shift Status | Medium | 36 hrs |
| Offline SQLite Database (Room DB) Architecture & DAO Setup | High | 52 hrs |
| Background Sync Engine using Android `WorkManager` (Bidirectional) | High | 64 hrs |
| Today's Job Queue, Schedule Calendar & Google Maps Navigation Intent | Medium | 40 hrs |
| Job Execution Flow (Acknowledge $\rightarrow$ En Route $\rightarrow$ Arrive $\rightarrow$ Start) | High | 48 hrs |
| Chemical/Material Usage Logging & Inspection Checklist | Medium | 36 hrs |
| CameraX Module with Local Image Compression ($<500\text{ KB}$ WebP) | High | 44 hrs |
| Customer Digital Signature Capture & COD Cash Collection Recording | Medium | 32 hrs |
| Job History & Daily Completion Performance Metrics | Low | 24 hrs |
| **Subtotal (Technician App)** | | **376 Hours** |

---

### 2.4 Web Admin ERP Dashboard (React 18 + TypeScript)

| Task / Module | Complexity | Dev Hours |
| :--- | :---: | :---: |
| React + TypeScript + Vite Scaffolding, Layout, Theme, Sidebar & Auth Routing | Medium | 36 hrs |
| Executive Dashboard (Live KPIs, Daily Bookings, Revenue, Active Techs) | High | 48 hrs |
| Booking Management: Table, Filter/Search, Detail Modal, Status Override | High | 56 hrs |
| Visual Dispatch Board (Technician Calendar/Gantt & Manual Reassignment) | High | 64 hrs |
| Service Catalog & Tiered Pricing Rules Configuration Engine | Medium | 40 hrs |
| Employee & Technician Management (Skills Matrix, Verification, Availability) | Medium | 40 hrs |
| Customer Management (Profile, Booking History, Addresses, Blacklisting) | Low | 28 hrs |
| Agency / Branch Management & Commission Configuration | Medium | 36 hrs |
| Expense Tracking Module (Category logging, receipt attachment) | Medium | 32 hrs |
| Invoice Browser, Payment Reconciliation & CSV/PDF Export | Medium | 36 hrs |
| Coupons & Promo Campaign Management | Low | 24 hrs |
| Support Ticket Desk & Low-Rating Escalation Center | Medium | 30 hrs |
| System Audit Log Explorer | Low | 20 hrs |
| **Subtotal (Admin Web ERP)** | | **490 Hours** |

---

### 2.5 Quality Assurance, Security, DevOps & Management

| Task / Module | Dev Hours |
| :--- | :---: |
| End-to-End API / Cloud Functions Integration Testing | 80 hrs |
| Mobile Device Compatibility & Offline Sync Stress Testing | 110 hrs |
| Security Penetration Testing & Firestore Rules Verification | 50 hrs |
| CI/CD Pipeline (GitHub Actions $\rightarrow$ Firebase App Distribution / Play Store Internal) | 40 hrs |
| Technical Documentation, Client Handover & Admin Training | 40 hrs |
| Project Management, Sprint Ceremonies & Backlog Grooming | 80 hrs |
| **Subtotal (QA, DevOps & PM)** | **400 Hours** |

---

### 📊 Total Development Effort Summary

```text
┌─────────────────────────────────────────────────────────────┐
│ Category                                       Effort (Hrs) │
├─────────────────────────────────────────────────────────────┤
│ 1. Backend, DB & Cloud Functions                    320 hrs │
│ 2. Customer Android App                             334 hrs │
│ 3. Technician Android App (Offline-First)           376 hrs │
│ 4. Web Admin ERP Dashboard                          490 hrs │
│ 5. QA, DevOps, Security & PM                        400 hrs │
├─────────────────────────────────────────────────────────────┤
│ TOTAL MVP DEVELOPMENT EFFORT                      1,920 hrs │
└─────────────────────────────────────────────────────────────┘
```

---

# 3. Required Manpower, Team Size & Skill Sets

To deliver the project in a **4-month (16-week)** window, the following **Core Agile Team** is recommended:

```text
                               ┌─────────────────────────────┐
                               │  Project Manager / Scrum    │
                               │  Master (0.5 FTE)           │
                               └──────────────┬──────────────┘
                                              │
                               ┌──────────────┴──────────────┐
                               │  Solutions Architect &      │
                               │  Tech Lead (0.5 FTE)        │
                               └──────────────┬──────────────┘
                                              │
         ┌──────────────────┬─────────────────┼──────────────────┬──────────────────┐
         │                  │                 │                  │                  │
         ▼                  ▼                 ▼                  ▼                  ▼
┌─────────────────┐┌─────────────────┐┌─────────────────┐┌─────────────────┐┌─────────────────┐
│ Sr. Android Dev ││ Mid Android Dev ││ Fullstack / Web ││ Backend / Cloud ││ QA & Automation │
│ (Technician App)││ (Customer App)  ││ Dev (React/TS)  ││ Dev (Firebase)  ││ Engineer        │
│ (1.0 FTE)       ││ (1.0 FTE)       ││ (1.0 FTE)       ││ (1.0 FTE)       ││ (1.0 FTE)       │
└─────────────────┘└─────────────────┘└─────────────────┘└─────────────────┘└─────────────────┘
```

### Detailed Role & Skill Set Matrix:

| Role | Allocation | Required Skill Set & Experience | Key Responsibilities |
| :--- | :---: | :--- | :--- |
| **Solutions Architect / Tech Lead** | 50% (Part-time) | • 8+ years experience<br>• Cloud Architecture & Security<br>• Distributed state machines<br>• Scalable NoSQL design | • System architecture & security rules<br>• Code reviews & performance oversight<br>• Concurrency & transaction design |
| **Senior Android Developer** | 100% (Full-time) | • 5+ years Java & Kotlin (Java 21)<br>• SQLite / Room DB & WorkManager<br>• CameraX & Image Compression<br>• Background services & battery optimization | • Technician App architecture<br>• Offline synchronization engine<br>• Hardware integration (Camera, GPS, Signature) |
| **Mid-Level Android Developer** | 100% (Full-time) | • 3+ years Android (Java/Kotlin)<br>• MVVM, Retrofit, Jetpack, Coroutines<br>• Google Maps SDK, OTP auto-fill<br>• Payment Gateway SDKs | • Customer App end-to-end UI & flows<br>• Checkout, Booking tracking & Invoices<br>• In-app feedback & support |
| **Frontend Web Developer** | 100% (Full-time) | • 4+ years React 18 & TypeScript<br>• TailwindCSS, Ant Design / Shadcn UI<br>• State management (Zustand/Redux Toolkit)<br>• Charting libraries (Recharts) | • Web Admin ERP Dashboard<br>• Interactive Dispatch & Gantt view<br>• Finance, Services, & User management screens |
| **Backend / Cloud Engineer** | 100% (Full-time) | • 4+ years Node.js & TypeScript<br>• Firebase Cloud Functions (v2)<br>• Cloud Firestore, Cloud Storage, FCM<br>• Payment Webhooks, PDF engines (PDFKit) | • Cloud Functions development<br>• Pricing, Invoicing, State transitions<br>• Scheduled cron tasks & aggregations |
| **QA / Automation Test Engineer** | 100% (Full-time) | • 3+ years Manual & Automation testing<br>• Android testing (Appium/Espresso)<br>• Postman / API load testing<br>• Offline resilience & network edge tests | • Test case authoring & execution<br>• Offline sync edge-case testing<br>• Regression & UAT verification |
| **UI/UX Designer** | 50% (First 6 wks) | • 4+ years UI/UX for Mobile & Web ERP<br>• Figma Design Systems & Prototyping<br>• Mobile UX for field staff | • High-fidelity Figma mockups<br>• Interactive click-through prototypes<br>• Design assets and icons |
| **Project Manager / Scrum Master**| 50% (Part-time) | • 5+ years Agile/Scrum delivery<br>• Jira / ClickUp sprint tracking<br>• Client stakeholder management | • Sprint planning & daily standups<br>• Milestone tracking & blocker removal<br>• Weekly client reporting |

---

# 4. Project Timeline, Milestones & Sprint Schedule

The project is structured into **8 two-week Sprints (16 Weeks Total)**:

```text
WEEKS:  01  02  03  04  05  06  07  08  09  10  11  12  13  14  15  16
        ├───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┤
        │ SPRINT 1 │ SPRINT 2 │ SPRINT 3 │ SPRINT 4 │ SPRINT 5 │ SPRINT 6 │ SPRINT 7 │ SPRINT 8 │
DESIGN  ██████████████                                                  
BACKEND ██████████████████████████████████████████                      
CUST APP        ██████████████████████████████████████                  
TECH APP        ██████████████████████████████████████████              
ADMIN WEB               ██████████████████████████████████████          
TESTING                         ████████████████████████████████████████
UAT/DEP                                                         ████████
```

### Sprint-by-Sprint Breakdown:

* **Sprint 1 (Weeks 1–2): Foundation & Design System**
  * Finalize Figma UI/UX for all 3 apps.
  * Initialize repositories, CI/CD, and Firebase environments (Dev, Staging).
  * Setup Base Database Schemas, Custom Claims Auth, and Base Android/React templates.

* **Sprint 2 (Weeks 3–4): Authentication, Catalog & Core Data Models**
  * Customer & Technician App Authentication (OTP, Google, PIN).
  * Admin Catalog management (Categories, Services, Pricing tiers).
  * Customer Service Browsing and Address management.

* **Sprint 3 (Weeks 5–6): Dynamic Pricing, Booking Flow & Dispatch Board**
  * Cloud Function pricing engine with coupon validation.
  * Customer Booking & Slot Selection UI.
  * Admin Dispatch Board (Manual Assignment & Technician availability filter).

* **Sprint 4 (Weeks 7–8): Technician Offline Core & Field Execution**
  * Technician SQLite Room database & `WorkManager` background queue.
  * Technician Job workflow: Accept $\rightarrow$ Start $\rightarrow$ Material log.
  * CameraX photo capture with local WebP compression.

* **Sprint 5 (Weeks 9–10): Payments, Billing & Invoicing Engine**
  * Payment gateway SDK integration (Customer App) + Webhook handling.
  * Cash on Delivery (COD) collection flow in Technician App.
  * Automated PDF invoice generation & email delivery Cloud Function.

* **Sprint 6 (Weeks 11–12): Admin ERP Modules & Customer History**
  * Admin Expense tracking, Agency setup, Customer desk, and Support tickets.
  * Customer Booking History, PDF downloads, and Review/Rating submission.
  * Technician daily metrics and completion summary.

* **Sprint 7 (Weeks 13–14): End-to-End Integration, Offline Stress & Security Audit**
  * Comprehensive offline sync stress testing (disconnects, slow 2G, battery kill).
  * Cloud Security Rules penetration audit and custom claims lock-down.
  * Admin dashboard KPI aggregations and reports export (CSV/PDF).

* **Sprint 8 (Weeks 15–16): UAT, Bug Fixing & Production Deployment**
  * User Acceptance Testing (UAT) with client team.
  * Production Firebase environment cutover & App Check activation.
  * Play Store Internal/Production build release & Web ERP domain hosting.
  * Admin training & handover documentation.

---

# 5. Comprehensive Cost Estimation

### 5.1 Engineering Manpower Cost Breakdown

*Rates are benchmarked at competitive global offshore/nearshore agency standards.*

| Role | Headcount | Hours / Week | Total Weeks | Total Hours | Blended Hourly Rate | Total Cost (USD) | Total Cost (INR Approx.) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tech Lead / Architect** | 1 (Part-time) | 20 hrs | 16 wks | 320 hrs | $00 / hr | $00,000 | ₹0,00,000 |
| **Sr. Android Dev (Tech App)** | 1 (Full-time) | 40 hrs | 16 wks | 640 hrs | $00 / hr | $00,000 | ₹00,00,000 |
| **Mid Android Dev (Cust App)** | 1 (Full-time) | 40 hrs | 14 wks | 560 hrs | $00 / hr | $0,000 | ₹0,00,000 |
| **Fullstack Web Dev (Admin)** | 1 (Full-time) | 40 hrs | 14 wks | 560 hrs | $00 / hr | $00,000 | ₹0,00,000 |
| **Backend / Cloud Engineer** | 1 (Full-time) | 40 hrs | 16 wks | 640 hrs | $00 / hr | $00,000 | ₹00,00,000 |
| **QA Automation Engineer** | 1 (Full-time) | 40 hrs | 12 wks | 480 hrs | $00 / hr | $0,000 | ₹0,00,000 |
| **UI/UX Designer** | 1 (Part-time) | 30 hrs | 6 wks | 180 hrs | $00 / hr | $0,000 | ₹0,00,000 |
| **Project Manager / Scrum** | 1 (Part-time) | 15 hrs | 16 wks | 240 hrs | $00 / hr | $0,000 | ₹0,00,000 |
| **Total Engineering Team** | **8 Members** | — | — | **3,620 Person-Hrs** | — | **$00,000\*** | **₹00,00,000\*** |

> \* **Dedicated Fixed-Price MVP Package Option:** When delivered by a dedicated cross-functional software agency using existing reusable modular scaffolds (auth, billing, dashboard templates), the total fixed-scope development package typically rationalizes to:
> **$00,000 – $00,000 USD (₹00,00,000 – ₹00,00,000 INR)**.

---

### 5.2 Cloud Infrastructure & Third-Party Recurring Costs (Monthly)

*Estimated for a scale of 1,000 to 5,000 bookings per month during the first year.*

| Service | Provider | Purpose | Monthly Cost (Est. USD) |
| :--- | :--- | :--- | :---: |
| **Firebase Blaze Plan** | Google Cloud | Firestore reads/writes, Cloud Functions, Cloud Storage, Hosting | $00 – $00 / mo |
| **Google Maps Platform** | Google Cloud | Geocoding API, Places Autocomplete, Static Map previews | $00 – $000 / mo |
| **Transactional SMS / OTP** | Twilio / MSG91 | Phone Number Login Verification OTPs ($0.005–$0.015/SMS) | $00 – $00 / mo |
| **Payment Gateway Fees** | Razorpay / Stripe | 1.8% – 2.5% per successful online transaction | *Deducted per txn* |
| **Google Play Developer** | Google | One-time Android Developer Account Registration | $00 (One-time) |
| **Domain, SSL & Web Host** | Cloudflare / Firebase | Custom domain DNS & SSL certificate | $00 – $00 / mo |
| **Transactional Email** | SendGrid / Resend | Invoice delivery & booking notification emails (Free tier up to 3k/mo) | $0 – $00 / mo |
| **Total Estimated Monthly Run-Rate** | | | **$000 – $000 / month** |

---

### 5.3 Total Cost of Ownership (TCO) Summary (Year 1)

```text
┌─────────────────────────────────────────────────────────────┬───────────────────────────┐
│ Expense Category                                            │ Year 1 Cost (USD)         │
├─────────────────────────────────────────────────────────────┼───────────────────────────┤
│ 1. Core ERP MVP Development (Fixed Scope / 16 Weeks)        │ $00,000 – $00,000         │
│ 2. Cloud Infrastructure & SaaS APIs (12 Months @ ~$000/mo)  │ $0,000                    │
│ 3. Post-Launch Warranty & Support (30 Days Included)        │ $0 (Included)             │
│ 4. Ongoing Maintenance & AMC (Optional: 15% of build/year)  │ $0,000 – $0,000 / year    │
├─────────────────────────────────────────────────────────────┼───────────────────────────┤
│ TOTAL ESTIMATED YEAR 1 INVESTMENT                           │ $00,000 – $00,000 USD     │
│ (INR Equivalent @ 00 INR/USD)                               │ ₹00.0L – ₹00.0L INR       │
└─────────────────────────────────────────────────────────────┴───────────────────────────┘
```

---

# 6. Assumptions, Risks & Contingency Plan

### Critical Assumptions:
1. **Design Approval Velocity:** UI/UX wireframes and visual design sign-off from the client will take no longer than 3 business days per review cycle.
2. **Third-Party Credentials:** Client will provide merchant accounts for Payment Gateway (Razorpay/Stripe), SMS Provider, and Google Cloud billing before Sprint 3.
3. **Android Target Hardware:** Technicians will use Android devices running Android 10 (API 29) or higher with camera and GPS support.

### Risk Management Matrix:

| Risk Identified | Impact | Probability | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **Offline Sync Conflicts** (Technician completes job offline, but admin cancelled online) | High | Medium | Implement timestamp priority in Cloud Functions: offline completion logs override cancellations if physical service started before cancellation timestamp. |
| **Firebase Read/Write Cost Spike** | Medium | Medium | Implement Firestore query caching, composite indexing, and daily pre-computed rollup metrics documents. |
| **Google Maps API Over-usage** | Low | Medium | Cache geocoding results locally in Firestore under `addresses` so recurring bookings to the same address make zero external API calls. |
| **Schedule Slippage due to Scope Creep** | High | Medium | Strictly adhere to the MVP scope boundary defined in Section 9 of the SRS; all non-critical feature additions logged to the Phase 2 backlog. |

---

*Document compiled for executive review, budget approval, and milestone planning.*
