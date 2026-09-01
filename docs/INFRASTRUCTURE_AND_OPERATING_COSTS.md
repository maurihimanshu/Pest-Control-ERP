# Pest Control ERP — Cloud Infrastructure & Operating Cost Analysis

**Document Version:** 1.0.0  
**Target Architecture:** Firebase Serverless + Google Cloud Platform + Third-Party SaaS  
**Date:** September 2026  
**Scope:** Excludes engineering manpower; covers 100% of cloud hosting, database, compute, storage, APIs, SMS gateways, and SaaS operating expenses.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Infrastructure Cost Matrix by Business Scale](#2-infrastructure-cost-matrix-by-business-scale)
3. [Itemized Component Breakdown](#3-itemized-component-breakdown)
   - [3.1 Firebase Backend & Database](#31-firebase-backend--database)
   - [3.2 Google Maps Platform & Geocoding](#32-google-maps-platform--geocoding)
   - [3.3 Transactional SMS & OTP Services](#33-transactional-sms--otp-services)
   - [3.4 Transactional Email & PDF Invoicing](#34-transactional-email--pdf-invoicing)
   - [3.5 Payment Gateway Platform Fees](#35-payment-gateway-platform-fees)
   - [3.6 Web Hosting, Domain & Security](#36-web-hosting-domain--security)
   - [3.7 One-Time Developer Registration Fees](#37-one-time-developer-registration-fees)
4. [Annual Total Cost of Ownership (TCO) Projections](#4-annual-total-cost-of-ownership-tco-projections)
5. [Cost Optimization Strategies](#5-cost-optimization-strategies)

---

# 1. Executive Summary

The **Pest Control ERP Platform** is designed on a **Serverless Event-Driven Cloud Architecture** leveraging Google Firebase and Google Cloud Platform (GCP).

### Key Commercial Advantages:
* **Zero Idle Server Costs:** No expensive dedicated virtual machines or idle database instances running 24/7.
* **Pay-As-You-Grow:** Cloud expenses scale directly in proportion to booking transaction volume.
* **Generous Free Tiers:** Significant free monthly quotas across Firebase and Google Maps mitigate early-stage operating expenses.

---

# 2. Infrastructure Cost Matrix by Business Scale

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           Monthly Cloud Infrastructure Cost Matrix                              │
├───────────────────────────────┬─────────────────────────┬─────────────────────┬─────────────────┤
│ Operational Scale             │ Monthly Volume          │ Monthly Cost (USD)  │ Monthly (INR)   │
├───────────────────────────────┼─────────────────────────┼─────────────────────┼─────────────────┤
│ Stage 1: Pilot & Launch       │ Up to 500 bookings/mo   │ $15 – $40 / mo      │ ₹1,200 – ₹3,300 │
│ Stage 2: Standard MVP Scale   │ 1,000 – 3,000 bookings  │ $60 – $150 / mo     │ ₹5,000 – ₹12,500│
│ Stage 3: Growth Stage         │ 5,000 – 10,000 bookings │ $180 – $350 / mo    │ ₹15,000 – ₹29,00│
│ Stage 4: High Enterprise Scale│ 25,000+ bookings/mo     │ $550 – $900 / mo    │ ₹45,000 – ₹75,00│
└───────────────────────────────┴─────────────────────────┴─────────────────────┴─────────────────┘
```

---

# 3. Itemized Component Breakdown

### 3.1 Firebase Backend & Database

| Component | Free Monthly Quota | Pricing Beyond Free Tier | Est. Monthly Cost (at 2,500 Bookings) |
| :--- | :--- | :--- | :---: |
| **Cloud Firestore** | • 50,000 reads / day<br>• 20,000 writes / day<br>• 1 GB total storage | • \$0.06 / 100k reads<br>• \$0.18 / 100k writes<br>• \$0.18 / GB / month | **$10 – $35 / mo** |
| **Cloud Functions (v2)** | • 2,000,000 invocations / mo<br>• 400,000 GB-seconds compute | • \$0.40 / million calls<br>• Standard CPU/memory rates | **$0 – $15 / mo** |
| **Cloud Storage** | • 5 GB stored data<br>• 1 GB download / day | • \$0.026 / GB / month<br>• \$0.12 / GB network egress | **$2 – $10 / mo** |
| **Firebase Cloud Messaging (FCM)**| • Unlimited Push Notifications | **100% Free Forever** | **$0.00** |
| **Firebase Authentication** | • Email/Password: Unlimited<br>• Google Sign-in: Unlimited | • Phone Auth: 10k free/mo, then \$0.01–\$0.06 / verification | **$0 – $10 / mo** |
| **Firebase Web Hosting** | • 10 GB storage<br>• 360 MB / day bandwidth | • \$0.026 / GB storage<br>• \$0.15 / GB transfer | **$0 – $2 / mo** |

---

### 3.2 Google Maps Platform & Geocoding

Google Cloud provides a recurring **$200 USD monthly free credit** applied automatically to every billing account.

* **Places API (Autocomplete):** Used in Customer App when adding/searching addresses (~$2.83 per 1,000 sessions).
* **Geocoding API:** Converts GPS coordinates to postal addresses (~$5.00 per 1,000 calls).
* **Optimization:** Customer addresses are cached locally in Firestore upon first entry. Repeat bookings to existing addresses consume **zero** Maps API calls.
* **Estimated Net Cost (after $200 free credit):** **$0 – $30 / month**.

---

### 3.3 Transactional SMS & OTP Services

Used for instant mobile login OTPs, booking confirmation alerts, and critical technician dispatch updates.

| Region / Provider | Unit Price per SMS | Est. Volume (2,500 Bookings) | Est. Monthly Cost |
| :--- | :--- | :--- | :---: |
| **India (MSG91 / Fast2SMS / DLT)** | ₹0.15 – ₹0.22 per SMS | ~8,000 SMS / month | **₹1,200 – ₹1,800 / mo** (~$15 – $22) |
| **International (Twilio)** | $0.0075 – $0.015 per SMS | ~3,000 SMS / month | **$25 – $45 / mo** |

---

### 3.4 Transactional Email & PDF Invoicing

Used for automated dispatch of tax invoices, receipts, and account notifications.

* **Provider Options:** Resend, SendGrid, or AWS SES.
* **Free Tiers:** Resend provides **3,000 free emails / month**; SendGrid provides 100 free emails / day.
* **Estimated Cost:** **$0 – $15 / month**.

---

### 3.5 Payment Gateway Platform Fees

* **Providers:** Razorpay / Stripe / Cashfree.
* **Fixed Infrastructure Charge:** **$0 / Month** (No monthly software or maintenance fees).
* **Transaction Fee:** Deducted automatically per successful online payment (typically **1.8% to 2.2%** + applicable taxes).

---

### 3.6 Web Hosting, Domain & Security

* **Domain Registration (.com / .in / .co):** ~$12 – $15 / year (**~$1.20 / month**).
* **SSL Certificate & CDN Caching:** **$0 / Free** (Managed automatically via Cloudflare / Firebase SSL).
* **Web Admin ERP App Hosting:** **$0 / Free** (Included in Firebase Hosting free tier).

---

### 3.7 One-Time Developer Registration Fees

* **Google Play Developer Account (Android):** **$25 USD (One-time lifetime fee)** to publish Customer and Technician apps.

---

# 4. Annual Total Cost of Ownership (TCO) Projections

### Year 1 Infrastructure Budget (Excluding Manpower)

```text
┌─────────────────────────────────────────────────────────────────────────┬─────────────────────────┐
│ Expense Category                                                        │ Annual Projected Cost   │
├─────────────────────────────────────────────────────────────────────────┼─────────────────────────┤
│ Google Play Developer Registration (One-Time)                           │ $25 USD                 │
│ Domain Name (.com / .in)                                                │ $15 USD                 │
│ Cloud Infrastructure (Firebase Blaze Tier @ ~$80/mo average)            │ $960 USD                │
│ Google Maps Platform (Net after $200/mo credit @ ~$15/mo)               │ $180 USD                │
│ Transactional SMS / OTP Gateway (@ ~$30/mo average)                     │ $360 USD                │
│ Transactional Email & Invoicing Service (@ ~$10/mo average)             │ $120 USD                │
├─────────────────────────────────────────────────────────────────────────┼─────────────────────────┤
│ TOTAL YEAR 1 INFRASTRUCTURE OPERATING COST                              │ ~$1,660 USD             │
│ (In INR: Approx. ₹1,35,000 – ₹1,50,000 for the full year)               │                         │
└─────────────────────────────────────────────────────────────────────────┴─────────────────────────┘
```

---

# 5. Cost Optimization Strategies

To ensure ongoing cloud bills remain minimal as the business scales, the following technical safeguards are built into the architecture:

1. **Client-Side Image Compression:** All service photos captured by technicians are converted locally to WebP format ($< 500\text{ KB}$) before upload, reducing Cloud Storage and egress bandwidth costs by $>80\%$.
2. **Address & Catalog Caching:** Customer addresses, active service categories, and base prices are cached locally on client devices, reducing repetitive Firestore document read operations.
3. **Aggregated Metric Rollups:** Executive KPI counters and daily financial reports are pre-calculated via scheduled Cloud Functions into single summary documents, preventing thousands of expensive document scans on each admin dashboard load.
4. **Push-First Notifications:** Free Firebase Cloud Messaging (FCM) is prioritized for in-app updates, reserving paid SMS credits strictly for initial OTP login verification.

---

*Compiled for enterprise financial planning and operational budget allocation.*
