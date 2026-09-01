# Cloud Infrastructure & Operating Cost Analysis
## Spring Boot, Managed PostgreSQL, Redis, RabbitMQ & Third-Party Services

**Document Version:** 2.0.0  
**Target Architecture:** Containerized Spring Boot + PostgreSQL + Redis + RabbitMQ + Object Storage  
**Date:** September 2026  
**Scope:** Excludes engineering manpower; covers 100% of server compute, database, caching, message broker, storage, APIs, SMS gateways, and SaaS operating expenses.

---

## 1. Executive Summary & Cost Philosophy

The **Pest Control ERP Platform** runs as a containerized Spring Boot Modular Monolith backed by PostgreSQL, Redis, and RabbitMQ.

### Key Cost Advantages:
* **Predictable VPS / Cloud Hosting:** Core application containers and database run on predictable, fixed-cost cloud compute rather than unpredictable pay-per-execution serverless billing.
* **Provider-Neutral Storage:** Object storage for photos and invoices uses cost-effective S3-compatible storage ($0.015–$0.025 / GB / month).
* **Minimal Third-Party SaaS:** Push notifications (FCM) are free; Google Maps costs are offset by the $200 recurring monthly credit.

---

## 2. Infrastructure Cost Matrix by Business Scale

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

## 3. Itemized Component Breakdown (Standard Production Scale: ~2,500 Bookings/Month)

| Component / Service | Recommended Provider / Spec | Purpose | Monthly Cost (USD) |
| :--- | :--- | :--- | :---: |
| **App Server (Spring Boot)** | 4 vCPU, 8 GB RAM (Hetzner / AWS / DigitalOcean)| Runs containerized Spring Boot & Nginx | **$25 – $50 / mo** |
| **PostgreSQL Database** | Managed PostgreSQL (2 vCPU, 4 GB RAM, 50 GB SSD)| Primary System-of-Record & WAL backups | **$30 – $60 / mo** |
| **Redis & RabbitMQ** | Containerized on App Server or Small Managed Node | Cache, distributed locks, async message broker| **$10 – $25 / mo** |
| **Object Storage (Photos/PDFs)**| AWS S3 / Cloudflare R2 / Google Cloud Storage | Inspection photos ($<500\text{ KB}$ WebP) & Invoices| **$5 – $15 / mo** |
| **Google Maps Platform** | Geocoding & Places Autocomplete | Address search (Covered by $200 free credit) | **$0 – $20 / mo** |
| **Transactional SMS / OTP** | MSG91 / Twilio / Fast2SMS | Customer OTPs (~8,000 SMS @ ₹0.18/SMS) | **$18 – $30 / mo** |
| **Transactional Email** | Resend / SendGrid (Free tier up to 3k/mo) | Invoice delivery & alerts | **$0 – $10 / mo** |
| **Domain, SSL & CDN** | Cloudflare Free Tier + Namecheap Domain | DDoS protection, SSL certificate & DNS | **~$1.20 / mo** |
| **Firebase Auth & FCM** | Google Firebase (Spark / Blaze Tier) | Identity provider & push alerts | **$0 / Free** |
| **Google Play Developer Console**| Google | One-time Android publishing fee | **$25 (One-time)** |

---

## 4. Annual Total Cost of Ownership (Year 1 Infra Budget)

```text
┌─────────────────────────────────────────────────────────────────────────┬─────────────────────────┐
│ Expense Category                                                        │ Annual Projected Cost   │
├─────────────────────────────────────────────────────────────────────────┼─────────────────────────┤
│ Google Play Developer Registration (One-Time)                           │ $25 USD                 │
│ Domain Name (.com / .in)                                                │ $15 USD                 │
│ Cloud Compute & Database (Spring Boot + Postgres @ ~$80/mo average)     │ $960 USD                │
│ Redis, RabbitMQ & Object Storage (@ ~$25/mo average)                    │ $300 USD                │
│ Transactional SMS / OTP Gateway (@ ~$25/mo average)                     │ $300 USD                │
│ Transactional Email & Maps API Buffer (@ ~$15/mo average)                │ $180 USD                │
├─────────────────────────────────────────────────────────────────────────┼─────────────────────────┤
│ TOTAL YEAR 1 INFRASTRUCTURE OPERATING COST                              │ ~$1,780 USD             │
│ (In INR: Approx. ₹1,45,000 – ₹1,60,000 for the full year)               │                         │
└─────────────────────────────────────────────────────────────────────────┴─────────────────────────┘
```

---

*Compiled for enterprise financial planning and server compute budgeting.*
