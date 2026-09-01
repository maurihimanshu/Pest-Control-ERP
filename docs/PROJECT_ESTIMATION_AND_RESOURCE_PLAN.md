# Project Estimation, Resource Plan & Timeline
## Spring Boot Modular Monolith, PostgreSQL & Multi-Platform ERP

**Document Version:** 2.0.0  
**Backend Framework:** Java 21 + Spring Boot 3.3.x (Maven)  
**Database & Messaging:** PostgreSQL 16, Redis 7.2, RabbitMQ 3.13  
**Client Applications:** Customer Android (Java 21), Technician Android (Java 21), Admin Web (React 18 + TS)  
**Date:** September 2026  

---

## 1. Executive Summary & Delivery Approach

This document outlines the **resource allocation, team composition, manpower skill requirements, effort estimates, and budget projections** for building the Pest Control ERP using a **Java 21 + Spring Boot Modular Monolith** and PostgreSQL architecture.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Project Metric Summary                                 │
├──────────────────────────────────────┬─────────────────────────────────────────────────┤
│ Total Estimated Engineering Effort   │ 2,080 Hours (~260 Man-Days)                     │
│ Core Team Size                       │ 6 Full-Time Professionals + 2 Part-Time / Lead  │
│ Release 1 (Core Operations) Timeline │ 12 Weeks (6 Sprints)                            │
│ Release 2 (Financials & Field ERP)   │ 6 Weeks (3 Sprints)                             │
│ Release 3 (AMC & Business Automation)│ 6 Weeks (3 Sprints)                             │
│ Total Full-Product Delivery Timeline │ 24 Weeks (6 Calendar Months)                    │
│ Estimated Full Development Cost      │ $38,000 – $48,000 (INR ₹31.5L – ₹40.0L approx.) │
│ Estimated Monthly Cloud/Server Cost  │ $85 – $220 / month                              │
└──────────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

## 2. Work Breakdown Structure (WBS) & Effort Estimation

### 2.1 Backend Core & Spring Boot Modules (Java 21 / Maven)

| Task / Module | Complexity | Dev Hours |
| :--- | :---: | :---: |
| Spring Boot Scaffolding, Maven Multi-Module / Package Structure & Config | Medium | 32 hrs |
| Flyway Database Migrations & PostgreSQL Schema (V1–V6 DDL Scripts) | High | 48 hrs |
| Spring Security + Firebase Authentication Token Filter & RBAC Matrix | High | 44 hrs |
| Service Catalog & Dynamic Pricing Engine (`PricingService`) | High | 50 hrs |
| 3-Tier Booking, Work Order & Service Visit State Machine Engine | High | 64 hrs |
| Redis Distributed Locking (`Redisson`) for Slot Reservations & Cache Config | Medium | 36 hrs |
| RabbitMQ Event Exchange, Queue Listeners & Async Decoupling | High | 44 hrs |
| Payment Gateway Integration (Razorpay/Stripe Webhooks + Signature Verify) | High | 40 hrs |
| Automated PDF Invoice Builder (OpenPDF/iText) & Object Storage Upload | Medium | 36 hrs |
| Chemical Inventory, Batch Expiry (FIFO) & Material Consumption Engine | High | 48 hrs |
| AMC Contract & Scheduled Visit Generator (Spring Scheduler Cron) | Medium | 36 hrs |
| Multi-Channel Notification Dispatcher (FCM, SMS, Email Thymeleaf) | Medium | 32 hrs |
| Daily Financial Rollup Aggregator & Reporting Endpoints | Medium | 36 hrs |
| Springdoc OpenAPI (Swagger UI) Configuration & Actuator Metrics | Low | 20 hrs |
| **Subtotal (Backend & Infrastructure)** | | **566 Hours** |

---

### 2.2 Customer Android Application (Java 21)

| Task / Module | Complexity | Dev Hours |
| :--- | :---: | :---: |
| App Setup, Navigation, Jetpack ViewBinding, Retrofit REST Client & Theme | Medium | 36 hrs |
| Phone Number OTP + Google Sign-In Auth (Firebase SDK) & User Profile | Medium | 40 hrs |
| Multi-Address Book with Google Maps Geocoding & Places Autocomplete | Medium | 36 hrs |
| Service Catalog Hierarchical Browser & Dynamic Pricing Summary Card | Medium | 32 hrs |
| Slot Picker, Dynamic Rate Summary & Checkout Flow | High | 48 hrs |
| Payment Gateway SDK Integration (UPI, Cards, Netbanking) & COD Flow | High | 44 hrs |
| Real-Time Booking Tracking Timeline & FCM Push Notification Receiver | Medium | 36 hrs |
| Service History, Invoice PDF Download & Review/Rating Submission | Medium | 36 hrs |
| In-App Customer Support Ticket Desk | Low | 24 hrs |
| **Subtotal (Customer App)** | | **332 Hours** |

---

### 2.3 Technician Android Application (Offline-First, Java 21)

| Task / Module | Complexity | Dev Hours |
| :--- | :---: | :---: |
| App Scaffolding, Device UUID Pairing, Secure PIN Login & Shift Status | Medium | 36 hrs |
| Offline SQLite Database (Room DB + SQLCipher) Architecture & DAO Setup | High | 54 hrs |
| Background Synchronization Engine (`WorkManager` with network constraint) | High | 64 hrs |
| Today's Assigned Job Queue, Daily Schedule & Google Maps Navigation Intent | Medium | 40 hrs |
| Job Execution Workflow (Acknowledge $\rightarrow$ En Route $\rightarrow$ Arrive $\rightarrow$ Start) | High | 48 hrs |
| Chemical/Material Consumption Logging & Pre-Service Safety Checklist | Medium | 36 hrs |
| CameraX Photo Capture with Local WebP Compression ($<500\text{ KB}$) | High | 44 hrs |
| Customer Digital Signature Capture & COD Cash Collection Recording | Medium | 32 hrs |
| Job History & Daily Completion Performance Metrics | Low | 24 hrs |
| **Subtotal (Technician App)** | | **378 Hours** |

---

### 2.4 Web Admin ERP Dashboard (React 18 + TypeScript)

| Task / Module | Complexity | Dev Hours |
| :--- | :---: | :---: |
| React + TypeScript + Vite Setup, Layout, Sidebar, Theme & Protected Routes | Medium | 36 hrs |
| Executive Dashboard (Live KPIs, Daily Bookings, Active Techs, Quick Actions)| High | 48 hrs |
| Booking Management: Table, Filter/Search, Detail Modal, Status Override | High | 56 hrs |
| Visual Dispatch Board (Gantt/Calendar View, Manual Reassignment) | High | 64 hrs |
| Service Catalog & Tiered Pricing Rules Configuration Engine | Medium | 40 hrs |
| Employee & Technician Management (Skills Matrix, Verification, Availability) | Medium | 40 hrs |
| Customer Management (Profile, Booking History, Addresses, Blacklisting) | Low | 28 hrs |
| Agency / Branch Management & Commission Configuration | Medium | 36 hrs |
| Chemical Inventory Console (Batch Receiving, Expiry Alerts, Trunk Stock) | High | 44 hrs |
| AMC Contract Management Console (Contract creation, Schedule viewer) | Medium | 36 hrs |
| Branch Expense Logging & Operational Profit & Loss (P&L) Reports | Medium | 36 hrs |
| Invoice Browser, Payment Reconciliation & CSV/PDF Export | Medium | 36 hrs |
| Support Ticket Desk & Audit Log Explorer | Low | 28 hrs |
| **Subtotal (Admin Web ERP)** | | **528 Hours** |

---

### 2.5 Quality Assurance, DevOps & Project Governance

| Task / Module | Dev Hours |
| :--- | :---: |
| Spring Boot Integration Tests with Testcontainers (Postgres, Redis, RabbitMQ) | 90 hrs |
| Mobile Offline Synchronization Stress Testing & Room Migration Verification | 100 hrs |
| Docker Multi-Stage Builds, Nginx Config & GitHub Actions CI/CD Pipeline | 46 hrs |
| Technical Documentation, Client Handover & Admin Training | 40 hrs |
| Project Management, Sprint Ceremonies & Backlog Governance | 80 hrs |
| **Subtotal (QA, DevOps & PM)** | **356 Hours** |

---

### 📊 Total Engineering Effort Summary: **2,160 Hours**

---

## 3. Required Manpower & Skill Matrix

```text
┌──────────────────────────────────────┬────────────┬─────────────────────────────────────────────────┐
│ Role                                 │ Allocation │ Required Skill Set & Experience                 │
├──────────────────────────────────────┼────────────┼─────────────────────────────────────────────────┤
│ **Solutions Architect / Tech Lead**  │ 50% (Part) │ Java 21, Spring Boot 3, PostgreSQL, Redis, RabbitMQ│
│ **Senior Backend Engineer**          │ 100% (Full)│ Java 21, Spring Boot, JPA/Hibernate, Flyway, Docker│
│ **Senior Android Engineer (Tech App)│ 100% (Full)│ Java 21, SQLite Room DB, WorkManager, CameraX   │
│ **Mid Android Engineer (Cust App)**  │ 100% (Full)│ Java 21, MVVM, Retrofit, Maps SDK, OTP Autofill │
│ **Senior Frontend Engineer (Admin)** │ 100% (Full)│ React 18, TypeScript, TailwindCSS, Ant Design   │
│ **QA Automation Engineer**           │ 100% (Full)│ Testcontainers, JUnit 5, Espresso, Playwright   │
│ **UI/UX Designer**                   │ 50% (6 wks)│ Figma, Design System, Mobile & Web ERP UX       │
│ **Project Manager / Scrum Master**   │ 50% (Part) │ Agile/Scrum, Jira, Sprint Ceremonies, Risk Mgmt │
└──────────────────────────────────────┴────────────┴─────────────────────────────────────────────────┘
```

---

*Governed by enterprise software estimation frameworks and agile delivery benchmarks.*
