# Cloud Infrastructure & Operating Cost Analysis
## Spring Boot, Managed PostgreSQL, Redis, RabbitMQ & Third-Party Services

**Document Version:** 2.1.0  
**Target Architecture:** Containerized Spring Boot 3.3 + PostgreSQL 16 + Redis 7.2 + RabbitMQ 3.13 + Object Storage  
**Date:** September 2026  
**Scope:** Excludes engineering manpower; covers 100% of server compute, database, caching, message broker, storage, APIs, SMS gateways, and SaaS operating expenses.

---

## Table of Contents

1. [Executive Summary & Cost Philosophy](#1-executive-summary--cost-philosophy)
2. [Infrastructure Cost Matrix by Business Scale](#2-infrastructure-cost-matrix-by-business-scale)
3. [Itemized Infrastructure Cost Categories](#3-itemized-infrastructure-cost-categories)
   - [3.1 Fixed Core Infrastructure](#31-fixed-core-infrastructure)
   - [3.2 Usage-Based Third-Party Services & APIs](#32-usage-based-third-party-services--apis)
4. [Annual Total Cost of Ownership (TCO) Projections](#4-annual-total-cost-of-ownership-tco-projections)
5. [Assumptions & Cost Management Guidelines](#5-assumptions--cost-management-guidelines)

---

> **PLANNING ESTIMATES NOTICE:** All figures in this document represent baseline engineering planning estimates, not formal vendor contractual quotations. Actual commercial operating costs will vary based on selected cloud regions, High Availability (HA) topologies, data retention policies, and negotiated third-party API volume pricing.

### Key Cost & Architecture Assumptions:
* **Predictable VPS / Cloud Hosting:** Core application containers and database run on predictable, fixed-cost cloud compute rather than unpredictable pay-per-execution serverless billing.
* **High Availability (HA) Evolution:** Stage 1–2 assume single-node managed database with automated daily snapshots. Stages 3–4 budget for active-standby PostgreSQL replication, Redis Sentinel failover, and clustered RabbitMQ nodes.
* **Provider-Neutral Storage & Egress:** Object storage for photos and invoices uses cost-effective S3-compatible storage ($0.015–$0.025 / GB / month) with pre-upload WebP compression (< 500 KB) keeping egress bandwidth minimal.
* **Retention Policies:** Operational logs (Prometheus/Loki) are retained for 30 days hot storage; PostgreSQL WAL archives and invoice PDFs are retained for 7 years on cold/archival tiers.
* **Minimal Third-Party SaaS:** Push notifications (FCM) are free; Google Maps costs are offset by the $200 recurring monthly credit.

---

# 2. Infrastructure Cost Matrix by Business Scale

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           Monthly Cloud Infrastructure Cost Matrix                              │
├───────────────────────────────┬─────────────────────────┬─────────────────────┬─────────────────┤
│ Operational Scale             │ Monthly Volume          │ Monthly Cost (USD)  │ Monthly (INR)   │
├───────────────────────────────┼─────────────────────────┼─────────────────────┼─────────────────┤
│ Stage 1: Pilot & Launch       │ Up to 500 bookings/mo   │ $45 – $75 / mo      │ ₹3,700 – ₹6,200 │
│ Stage 2: Standard Production  │ 1,000 – 3,000 bookings  │ $85 – $180 / mo     │ ₹7,000 – ₹15,000│
│ Stage 3: Growth Stage         │ 5,000 – 10,000 bookings │ $220 – $420 / mo    │ ₹18,000 – ₹35,00│
│ Stage 4: High Enterprise Scale│ 25,000+ bookings/mo     │ $550 – $950 / mo    │ ₹45,000 – ₹78,00│
└───────────────────────────────┴─────────────────────────┴─────────────────────┴─────────────────┘
```

---

# 3. Itemized Infrastructure Cost Categories

Costs are classified into **Fixed Infrastructure** (servers, database instances, backups) and **Usage-Based SaaS/APIs** (SMS, emails, geocoding, payment transactions).

### 3.1 Fixed Core Infrastructure

| Category | Recommended Provider / Spec | Purpose | Monthly Cost (USD) |
| :--- | :--- | :--- | :---: |
| **1. Spring Boot Compute** | 4 vCPU, 8 GB RAM (Hetzner / AWS / DigitalOcean)| Runs containerized Spring Boot & JVM | **$25 – $50 / mo** |
| **2. PostgreSQL Database** | Managed PostgreSQL 16 (2 vCPU, 4 GB RAM, 50 GB SSD)| Primary System-of-Record & ACID transactions | **$30 – $60 / mo** |
| **3. Redis In-Memory Cache** | Containerized or Small Managed Node (1 GB RAM) | Slot Redlock, rate limiting, catalog cache | **$5 – $15 / mo** |
| **4. RabbitMQ Broker** | Containerized on App Server or Managed Broker | Decoupled asynchronous event queues | **$5 – $15 / mo** |
| **5. Object Storage** | AWS S3 / Cloudflare R2 / Google Cloud Storage | Inspection photos ($<500\text{ KB}$ WebP) & Invoices| **$5 – $15 / mo** |
| **6. Load Balancer / Reverse Proxy**| Nginx Container + Cloudflare Edge | TLS 1.3 termination, gzip/brotli compression | **$0 – $10 / mo** |
| **7. Monitoring & Logging** | Spring Actuator + Prometheus + Grafana (Self-hosted)| Metrics scraping, health probes, structured logs | **$0 – $10 / mo** |
| **8. Backup & Disaster Recovery** | Automated Daily PostgreSQL WAL Snapshots + S3 Sync | Point-in-time recovery (PITR) with 30-day retention| **$5 – $15 / mo** |
| **9. Domain, TLS & Security** | Cloudflare Free Tier + Registrar (.com / .in) | DDoS protection, automated SSL certificates & DNS | **~$1.20 / mo** |
| **Fixed Infrastructure Subtotal**| | | **$76 – $191 / mo** |

---

### 3.2 Usage-Based Third-Party Services & APIs

| Category | Provider | Pricing Model & Free Allowance | Est. Monthly Cost (2,500 Bookings) |
| :--- | :--- | :--- | :---: |
| **10. Firebase Authentication** | Google Firebase | Free for Email/Password; Phone OTP has free quota | **$0 – $10 / mo** |
| **11. Firebase Cloud Messaging (FCM)**| Google Firebase | Unlimited push notifications to Android apps | **$0.00 / Free** |
| **12. Google Maps Platform** | Google Cloud Platform | Places Autocomplete & Geocoding (\$200/mo credit)| **$0 – $20 / mo** |
| **13. Transactional SMS / OTP** | MSG91 / Twilio / Fast2SMS | ~8,000 SMS @ ₹0.18–₹0.22 / SMS (India DLT) | **$18 – $30 / mo** |
| **14. Transactional Email** | SendGrid / Resend / AWS SES | HTML invoice delivery (Free tier up to 3k/mo) | **$0 – $10 / mo** |
| **15. Payment Gateway** | Razorpay / Stripe / Cashfree | 1.8% – 2.0% per successful online transaction | *Deducted per txn* |
| **Usage-Based Services Subtotal**| | | **$18 – $70 / mo** |

---

# 4. Annual Total Cost of Ownership (TCO) Projections

```text
┌─────────────────────────────────────────────────────────────────────────┬─────────────────────────┐
│ Expense Category                                                        │ Annual Projected Cost   │
├─────────────────────────────────────────────────────────────────────────┼─────────────────────────┤
│ Google Play Developer Registration (One-Time Fee)                       │ $25 USD                 │
│ Domain Name Registration (.com / .in)                                   │ $15 USD                 │
│ Fixed Cloud Infrastructure (Spring Boot + Postgres + Redis + RabbitMQ)  │ $1,080 – $1,800 USD     │
│ Object Storage, Backups & Disaster Recovery Storage                     │ $120 – $240 USD         │
│ Usage-Based SMS / OTP Gateway & Maps API Buffer                         │ $300 – $480 USD         │
│ Transactional Email & Invoicing Service Buffer                          │ $60 – $120 USD          │
├─────────────────────────────────────────────────────────────────────────┼─────────────────────────┤
│ TOTAL YEAR 1 INFRASTRUCTURE OPERATING BUDGET                            │ ~$1,600 – ~$2,680 USD   │
│ (In INR: Approx. ₹1,35,000 – ₹2,20,000 for the full year)               │                         │
└─────────────────────────────────────────────────────────────────────────┴─────────────────────────┘
```

---

# 5. Assumptions & Cost Management Guidelines

### Budget Assumptions:
1. **Google Maps Free Credit:** Assumes active Google Cloud billing account receiving the standard recurring $200 USD monthly credit. Customer addresses are cached locally to minimize redundant geocoding requests.
2. **Technician Image Compression:** Field photos taken with CameraX are compressed to WebP ($<500\text{ KB}$) on the device prior to upload, keeping Object Storage and egress bandwidth costs negligible.
3. **Database Sizing:** Estimated data generation is approximately 1.5 GB of relational data per 10,000 completed bookings. A 50 GB SSD provides over 2 years of transactional growth before disk expansion is required.

---

*Compiled for enterprise financial planning and infrastructure budgeting.*
