# Security Policy & Standards
## Pest Control Enterprise Resource Planning (ERP) Platform

**Document Version:** 2.0.0  
**Backend Framework:** Spring Security 6.3.x & Java 21  
**Database Security:** PostgreSQL 16 Encryption & Row Constraints  
**Identity Provider:** Firebase Authentication (ID Token Validation)  
**Date:** September 2026  

---

## Table of Contents

1. [Security Philosophy & Architecture](#1-security-philosophy--architecture)
2. [Reporting a Vulnerability / Responsible Disclosure](#2-reporting-a-vulnerability--responsible-disclosure)
3. [Authentication & Access Control (RBAC)](#3-authentication--access-control-rbac)
4. [Data Protection, Encryption & Privacy](#4-data-protection-encryption--privacy)
5. [Server-Side Logic & Anti-Tampering Safeguards](#5-server-side-logic--anti-tampering-safeguards)
6. [Offline Data Security on Field Devices](#6-offline-data-security-on-field-devices)
7. [Encryption & Transport Security](#7-encryption--transport-security)
8. [Payment Gateway & Financial Security](#8-payment-gateway--financial-security)
9. [Audit Logging & Non-Repudiation](#9-audit-logging--non-repudiation)
10. [Infrastructure Security & Rate Limiting](#10-infrastructure-security--rate-limiting)
11. [Incident Response & Security SLAs](#11-incident-response--security-slas)

---

# 1. Security Philosophy & Architecture

The **Pest Control ERP Platform** adheres to an enterprise **Zero-Trust Security Model** and the principle of **Least Privilege**. 

### Core Security Principles:
1. **Never Trust the Client:** Client applications (Customer Android, Technician Android, and React Admin Web) are treated as untrusted presentation layers. All pricing calculations, booking state progressions, permissions, inventory deductions, and invoice generation must be validated on the server via Spring Boot domain services and PostgreSQL transactions.
2. **Defense in Depth:** Security is enforced at multiple independent layers: network perimeter (Cloudflare/Nginx), application firewall, JWT token verification, Spring Security RBAC filters, SpEL method guards, and database constraints.
3. **Data Minimization:** Technicians and third-party integrations only receive the minimum PII necessary to perform their assigned physical tasks.

---

# 2. Reporting a Vulnerability / Responsible Disclosure

We take software security and customer privacy seriously. If you discover a security vulnerability or potential threat in this platform, please disclose it responsibly.

### How to Report:
* **Security Contact:** `security@yourcompany.com` (or submit via the private vulnerability reporting portal)
* **Information to Include:** Detailed description of the vulnerability, step-by-step proof-of-concept (PoC), affected component(s), and potential impact assessment.

### Our Commitment:
* **Acknowledgement:** Within **24 hours** of receipt.
* **Triage & Status Update:** Within **72 hours**.
* **Remediation SLA:** Critical vulnerabilities resolved within **7 business days**.
* **Safe Harbor:** We will not pursue legal action against security researchers who report issues in good faith without exfiltrating customer data, degrading service availability, or publicly disclosing issues before a patch is published.

---

# 3. Authentication & Access Control (RBAC)

### 3.1 Role-Based Access Control via Spring Security
User authorization is governed by **Spring Security** evaluating user roles loaded from PostgreSQL upon verifying the client's Firebase ID token.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            User Roles & Hierarchy                           │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ SUPER_ADMIN     │ Full system access, audit logs, financial reports, config │
│ ADMIN           │ Central operations manager, employee & service manager    │
│ DISPATCHER      │ Job assignment, booking management, technician scheduling │
│ AGENCY_MANAGER  │ Branch-specific technicians, local bookings, and expenses  │
│ ACCOUNTANT      │ Financial manager access to invoices, expenses, and P&L   │
│ TECHNICIAN      │ Assigned jobs only, service checklists, material logging  │
│ CUSTOMER        │ Self-service bookings, address book, invoices, reviews    │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### 3.2 Authentication Safeguards:
* **Customer Authentication:** Phone Number + OTP with rate-limiting (max 3 attempts per 10 minutes) to prevent SMS bombing and brute-force attacks.
* **Technician Authentication:** Mobile / Employee ID + PIN bound to the physical device UUID. If a device is reported lost or an employee is terminated, setting `users.is_active = false` immediately invalidates their session.
* **Admin Web Authentication:** Corporate Email + Password enforced with **Multi-Factor Authentication (MFA)** and automated session timeout after 30 minutes of inactivity.

**User Deactivation:**
When a user is deactivated (is_active = false in PostgreSQL), all subsequent API requests are rejected at the Spring Security filter level, regardless of Firebase token validity. Firebase token revocation is a separate identity-management concern. The ERP does not rely on Firebase token expiry as the primary deactivation mechanism.

**Firebase App Check (Play Integrity):**
The Android apps use Firebase App Check with the Play Integrity API provider to verify that requests originate from genuine, unmodified app binaries. Note: App Check is a client-integrity attestation layer — it is NOT a replacement for Spring Security authorization or Firebase Authentication. A valid App Check token does not authorize ERP operations; that is handled by the full authentication/authorization pipeline.

---

# 4. Data Protection, Encryption & Privacy

### 4.1 Data in Transit
* All API calls, WebSocket streams, and Object Storage uploads require **TLS 1.3 (HTTPS / WSS)** with HSTS enabled.
* Plaintext HTTP connections are automatically redirected or rejected at the Nginx reverse proxy.

### 4.2 Data at Rest
* **PostgreSQL Database:** Encrypted at rest using standard **AES-256** disk encryption (LUKS / AWS EBS / Managed Cloud SQL KMS).
* **Object Storage:** Customer photos, signed job sheets, and PDF invoices are stored encrypted with private access control.
* **Technician SQLite Database (Room):** Sensitive local offline queues and session tokens are encrypted on-device using Android Keystore and SQLCipher.

### 4.3 Personally Identifiable Information (PII) Redaction
* Customer phone numbers are masked when viewed in general reporting dashboards.
* Exact customer home addresses are hidden from technicians until the job status transitions to `TECHNICIAN_ACCEPTED` or `ON_THE_WAY`.

---

# 5. Server-Side Logic & Anti-Tampering Safeguards

To prevent client-side parameter tampering (e.g., modifying service rates, applying invalid coupon discounts, or skipping workflow steps):

1. **Server-Calculated Billing:** The client application transmits only `{ serviceId, pricingTier, couponCode }`. The Spring Boot `PricingService` fetches verified base rates from PostgreSQL and calculates totals on the server.
2. **Strict State Machine Transitions:** Bookings cannot transition to illegal states (e.g., `CONFIRMED` $\rightarrow$ `SERVICE_COMPLETED` without technician check-in). Transitions are guarded by transactional domain services.
3. **Database Security Constraints:** Foreign keys and check constraints ensure data integrity even in the event of software errors.

---

# 6. Offline Data Security on Field Devices

Because the Technician Android App is offline-first:

1. **Encrypted Local Storage:** Offline job data, service checklists, and customer signatures are cached in a sandboxed Room database encrypted with keys stored in the **Android Keystore System**.
2. **Cryptographic Payload Signing:** Each offline operation is assigned a deterministic operation_id (UUID), authenticated user JWT, and device_id. The server validates identity, enforces idempotency, and maintains a complete audit trail. Cryptographic payload signing is deferred to a future security hardening phase.
3. **Media Sandbox:** Photos taken via CameraX are written directly to the application-private directory (`Context.getExternalFilesDir()`) and deleted from the local cache immediately upon successful Object Storage sync.

---

# 7. Encryption & Transport Security

**Transport Security (TLS):**
All API communication uses TLS 1.2/1.3 enforced at the Nginx load balancer. Certificate rotation is automated via Let's Encrypt or equivalent.

**Data-at-Rest Encryption:**
PostgreSQL data-at-rest encryption is managed at the infrastructure/cloud provider level. Object Storage (S3/GCS) uses server-side encryption (SSE). Android local Room database uses SQLCipher with keys stored in the Android Keystore System.

**Important Terminology Clarification:**
This system does NOT implement End-to-End Encryption (E2EE). E2EE would require that encryption keys are held exclusively by the communicating endpoints and the server cannot decrypt the content. This ERP system intentionally processes business records server-side (pricing, booking state, inventory, payments) — this is correct for an ERP and is NOT a security gap.

The correct description is:
- TLS protects data in transit between clients and the backend
- Cloud/database encryption protects data at rest
- Android Keystore protects device-local data

---

# 8. Payment Gateway & Financial Security

1. **PCI-DSS Compliance:** The platform does not store or process raw credit/debit card numbers, CVVs, or banking credentials. All payments use tokenized gateway SDKs (Razorpay / Stripe / Cashfree).
2. **Webhook Signature Verification:** Payment confirmation webhooks require HMAC-SHA256 signature verification matching the gateway secret before updating any booking status.
3. **Idempotency Safeguards:** Every payment event is checked against unique `gateway_payment_id` constraints in PostgreSQL to guarantee transactions cannot be double-credited or replayed.
**Payment Event Idempotency:**
Each payment webhook event is tracked in the `payment_events` table with a UNIQUE constraint on `(provider, gateway_event_id)`. This ensures that multiple webhook deliveries of the same event (which payment gateways routinely retry) are processed exactly once. A single payment may generate multiple events (authorized, captured, failed, refunded) — these are all tracked separately.

---

# 9. Audit Logging & Non-Repudiation

An immutable, append-only audit trail (`audit_logs`) in PostgreSQL records all administrative and operational actions:

* Price adjustments, discount/coupon creation, and tax rule updates.
* Manual booking status overrides and technician reassignments.
* Expense approvals and agency commission modifications.
* Account deactivations and permission changes.

Each audit record captures: `timestamp`, `actorId`, `actorRole`, `action`, `entityType`, `entityId`, `oldValue`, `newValue`, and `ipAddress`.

---

# 10. Infrastructure Security & Rate Limiting

* **Redis Rate Limiter:** Protects public endpoints (such as OTP requests and login) against abuse using a sliding window algorithm in Redis.
* **CORS Policies:** Spring Security strictly enforces Cross-Origin Resource Sharing (CORS) whitelisting only the official Admin Web domain.
* **SQL Injection Prevention:** 100% of database access is mediated via Spring Data JPA / Hibernate parameterized queries.

---

# 11. Incident Response & Security SLAs

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Incident Severity & Response Matrix                   │
├──────────┬──────────────────────────────────────────┬───────────────────────┤
│ Severity │ Definition                               │ Target Response / Fix │
├──────────┼──────────────────────────────────────────┼───────────────────────┤
│ P1 - Crit│ Active data breach, auth bypass, RCE     │ < 2 hrs / < 12 hrs    │
│ P2 - High│ Privilege escalation, billing tamper risk │ < 8 hrs / < 48 hrs    │
│ P3 - Med │ Information leak without auth bypass     │ < 24 hrs / < 7 days   │
│ P4 - Low │ Minor misconfiguration, theoretical risk │ < 72 hrs / Next Sprint│
└──────────┴──────────────────────────────────────────┴───────────────────────┘
```

---

*Governed by OWASP Top 10, Spring Security standards, and enterprise data privacy regulations.*
