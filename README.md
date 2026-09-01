# 🐜 Enterprise Pest Control Management & ERP Platform
### Commercial & Technical Project Proposal

---

## 📌 Executive Summary

Modern pest control operations require seamless orchestration between customer acquisition, field technician dispatching, on-site service verification, inventory control, and financial reporting. 

This proposal presents a **centralized, digital-first Pest Control Enterprise Resource Planning (ERP) Platform**. The system unifies customer self-service, offline-capable field workforce management, and executive operational control into a secure, real-time cloud ecosystem.

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Unified ERP Ecosystem                                         │
├───────────────────────────────┬───────────────────────────────┬─────────────────────────────────┤
│    📱 Customer Android App    │    📱 Technician Android App  │       💻 Admin Web ERP          │
│  (Booking, Tracking, Payments)│ (Offline Jobs, Photos, Sign)  │  (Dispatch, Finances, Reports)  │
└───────────────────────────────┴───────────────────────────────┴─────────────────────────────────┘
                                                ▲
                                                │ (Real-Time Sync)
                                                ▼
                               ┌─────────────────────────────────┐
                               │     ☁️ Firebase Cloud Engine    │
                               │ (Auth, Firestore, Cloud Funcs)  │
                               └─────────────────────────────────┘
```

---

## 📂 Project Documentation Index

All detailed specifications, architecture designs, resource requirements, and cost models are available in the dedicated documentation suite:

| Document | Description | Direct Link |
| :--- | :--- | :--- |
| 📋 **Software Requirements Specification (SRS)** | Complete module-by-module functional requirements, database schema, RBAC matrix, Cloud Functions API, and security rules. | [**`docs/SOFTWARE_REQUIREMENTS_SPECIFICATION.md`**](./docs/SOFTWARE_REQUIREMENTS_SPECIFICATION.md) |
| ⏱️ **Project Estimation & Resource Plan** | Work Breakdown Structure (WBS), 16-week sprint schedule, manpower skill sets, and detailed cost breakdown. | [**`docs/PROJECT_ESTIMATION_AND_RESOURCE_PLAN.md`**](./docs/PROJECT_ESTIMATION_AND_RESOURCE_PLAN.md) |

---

## 🎯 Core Business Objectives & ROI

1. **Eliminate Revenue Leakage:** Automated pricing calculation, tamper-proof Cloud Function billing, and cash reconciliation eliminate manual billing errors and uncollected dues.
2. **Offline-Resilient Field Force:** Technicians can execute full treatment checklists, capture before/after photos, and obtain customer sign-offs in basements or remote zones with zero connectivity; the app auto-syncs when reconnected.
3. **Optimized Dispatch & Resource Allocation:** Real-time visual dispatch board prevents double-booking, matches technician skill certifications with service requirements, and reduces travel overhead.
4. **Enhanced Customer Retention:** Transparent real-time job tracking, digital PDF invoicing, service history, and support escalation improve customer satisfaction and recurring AMC renewals.
5. **Multi-Branch & Agency Scalability:** Architecture supports regional branches/agencies with segregated customer lists, technician teams, and commission settlements.

---

## 📱 System Applications Overview

### 1. Customer Android Application (Java 21 / Jetpack)
* **Instant Onboarding:** Mobile OTP login with automatic SMS detection.
* **Smart Booking Engine:** Multi-property address book with Google Maps pin placement and time-slot selection.
* **Transparent Pricing:** Dynamic breakdown of flat fees, area-based rates (sq. ft.), room configurations (BHK), and add-on treatments.
* **Live Job Tracking:** Real-time status progression from assignment to completion.
* **Flexible Payments:** Integrated payment gateway (Cards, UPI, Netbanking) and Cash on Delivery (COD).
* **Service Records:** In-app PDF invoice downloads, treatment histories, and rating submissions.

### 2. Field Technician Android Application (Offline-First, Java 21)
* **Secure Authentication:** Employee ID / Mobile with PIN and device UUID pairing.
* **Offline-First Workflow:** Full offline job execution powered by local SQLite (Room DB) and Android `WorkManager` background sync.
* **On-Site Verification:** Timestamped and geotagged before/after photo capture with automatic client-side WebP compression ($<500\text{ KB}$).
* **Material & Chemical Consumption Log:** Detailed chemical batch and dosage tracking per service visit.
* **Digital Sign-Off:** On-screen customer signature capture or OTP sign-off verification.

### 3. Web Admin ERP Dashboard (React 18 + TypeScript)
* **Executive Command Center:** Real-time KPI counters (Daily Bookings, Active Field Techs, Revenue vs Expenses).
* **Interactive Dispatch Board:** Gantt and calendar dispatch views with drag-and-drop manual reassignment.
* **Dynamic Service & Pricing Management:** Tiered rate management, promo coupons, and service category controls.
* **Operational Accounting:** Branch expense categorization, receipt uploads, and net operational margin tracking.
* **Automated Billing & Reporting:** Sequential invoice numbering (`INV-2026-XXXXX`), CSV/PDF financial export, and low-rating escalation desk.

---

## 🛠️ Technology Stack & Standards

| Layer | Technology | Key Capabilities |
| :--- | :--- | :--- |
| **Customer App** | Native Android (Java 21) | Android Jetpack, MVVM, Retrofit, Google Maps SDK, OTP Autofill |
| **Technician App** | Native Android (Java 21) | SQLite Room DB, `WorkManager`, CameraX, Offline Transaction Queue |
| **Admin Web ERP** | React 18 + TypeScript | Vite, TailwindCSS, Ant Design, Recharts, Responsive Grid Layout |
| **Backend & APIs** | Firebase Cloud Functions (v2) | Node.js 20, TypeScript, Serverless Callable Endpoints, Cron Schedulers |
| **Database** | Cloud Firestore | Scalable NoSQL, Atomic Transactions, Aggregation Rollups |
| **File Storage** | Firebase Cloud Storage | Encrypted PDF invoices, before/after service media |
| **Security & Auth** | Firebase Auth + Custom Claims | Zero-trust token-based RBAC, Firebase App Check |
| **Push Alerts** | Firebase Cloud Messaging (FCM) | Topic-based multicast notifications for customers, technicians, and dispatchers |

---

## 🗓️ Delivery Roadmap (16-Week MVP)

```text
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│   SPRINT 1   │   SPRINT 2   │   SPRINT 3   │   SPRINT 4   │   SPRINT 5   │   SPRINT 6   │   SPRINT 7   │   SPRINT 8   │
│  WEEKS 1–2   │  WEEKS 3–4   │  WEEKS 5–6   │  WEEKS 7–8   │  WEEKS 9–10  │ WEEKS 11–12  │ WEEKS 13–14  │ WEEKS 15–16  │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Architecture │ Auth & Master│ Dynamic Price│ Tech Offline │ Payments &   │ Admin ERP    │ Integration, │ UAT, Release │
│ & UI/UX Base │ Data Catalog │ & Dispatch   │ Queue & Cam  │ Invoicing    │ Financials   │ Stress & Sec │ & Deployment │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 💰 Investment & Commercial Summary

| Item | Details | Estimate |
| :--- | :--- | :--- |
| **MVP Development (Fixed Scope)** | Complete delivery of all 3 applications + Cloud Backend (16 Weeks) | **$00,000 – $00,000 USD**<br>*(₹00.0L – ₹00.0L INR)* |
| **Estimated Cloud & API Hosting** | Firebase Blaze, Google Maps API, SMS/OTP Gateway, Domain/SSL | **$000 – $000 / month** |
| **Warranty & Post-Launch Support** | Critical bug fixes and deployment monitoring | **30 Days Included** |
| **Annual Maintenance (Optional)** | SLA-backed support, security updates, and performance tuning | **15% of build cost / year** |

---

## 🚀 Next Steps & Project Kickoff

1. **Stakeholder Review & Sign-Off:** Review the [SRS Document](./docs/SOFTWARE_REQUIREMENTS_SPECIFICATION.md) and [Resource Plan](./docs/PROJECT_ESTIMATION_AND_RESOURCE_PLAN.md).
2. **Third-Party Account Provisioning:** Setup Firebase Organization, Google Cloud Console, and Payment Gateway sandbox keys.
3. **UI/UX Design Sprint Kickoff:** Finalize wireframes and brand design tokens for Customer and Admin applications.

---

*Prepared for Enterprise Management Review.*
