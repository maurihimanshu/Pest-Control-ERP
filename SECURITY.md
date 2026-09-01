# Security Policy & Standards
## Pest Control Enterprise Resource Planning (ERP) Platform

**Document Version:** 1.0.0  
**Effective Date:** September 2026  
**Target Systems:** Customer Android App, Technician Android App, Admin Web ERP Dashboard, Firebase Cloud Backend  

---

## Table of Contents

1. [Security Philosophy & Architecture](#1-security-philosophy--architecture)
2. [Reporting a Vulnerability / Responsible Disclosure](#2-reporting-a-vulnerability--responsible-disclosure)
3. [Authentication & Access Control (RBAC)](#3-authentication--access-control-rbac)
4. [Data Protection, Encryption & Privacy](#4-data-protection-encryption--privacy)
5. [Server-Side Logic & Anti-Tampering Safeguards](#5-server-side-logic--anti-tampering-safeguards)
6. [Offline Data Security on Field Devices](#6-offline-data-security-on-field-devices)
7. [Payment Gateway & Financial Security](#7-payment-gateway--financial-security)
8. [Audit Logging & Non-Repudiation](#8-audit-logging--non-repudiation)
9. [Infrastructure Security & App Integrity](#9-infrastructure-security--app-integrity)
10. [Incident Response & Security SLAs](#10-incident-response--security-slas)

---

# 1. Security Philosophy & Architecture

The **Pest Control ERP Platform** adheres to an enterprise **Zero-Trust Security Model** and the principle of **Least Privilege**. 

### Core Security Principles:
1. **Never Trust the Client:** Client applications (Customer Android, Technician Android, and React Admin Web) are treated as untrusted presentation layers. All pricing calculations, booking state progressions, permissions, and invoice generation must be validated on the server via Firebase Cloud Functions and Firestore Transactions.
2. **Defense in Depth:** Security is enforced at multiple independent layers: network perimeter, application firewall, JWT custom claims, Firestore database rules, and encrypted storage.
3. **Data Minimization:** Technicians and third-party integrations only receive the minimum PII necessary to perform their assigned physical tasks.

---

# 2. Reporting a Vulnerability / Responsible Disclosure

We take software security and customer privacy seriously. If you discover a security vulnerability or potential threat in this platform, please disclose it responsibly.

### How to Report:
* **Security Contact:** `security@yourcompany.com` (or submit via the private vulnerability reporting portal)
* **Encryption:** Please use our PGP public key for sensitive disclosures.
* **Information to Include:**
  * Detailed description of the vulnerability.
  * Step-by-step proof-of-concept (PoC) or reproduction steps.
  * Affected component(s) (Customer App, Technician App, Admin Portal, Cloud Functions, Firestore Rules).
  * Potential impact assessment.

### Our Commitment:
* **Acknowledgement:** Within **24 hours** of receipt.
* **Triage & Status Update:** Within **72 hours**.
* **Remediation SLA:** Critical vulnerabilities resolved within **7 business days**.
* **Safe Harbor:** We will not pursue legal action against security researchers who report issues in good faith without exfiltrating customer data, degrading service availability, or publicly disclosing issues before a patch is published.

---

# 3. Authentication & Access Control (RBAC)

### 3.1 Role-Based Access Control via Custom Claims
User authorization is governed by **Firebase Auth Custom Claims** (`token.claims.role`), embedded directly inside cryptographically signed JSON Web Tokens (JWTs).

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            User Roles & Hierarchy                           │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ SUPER_ADMIN     │ Full system access, audit logs, financial reports, config │
│ DISPATCHER      │ Job assignment, booking management, technician scheduling │
│ AGENCY_MANAGER  │ Branch-specific technicians, local bookings, and expenses  │
│ TECHNICIAN      │ Assigned jobs only, service checklists, material logging  │
│ CUSTOMER        │ Self-service bookings, address book, invoices, reviews    │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### 3.2 Authentication Safeguards:
* **Customer Authentication:** Phone Number + OTP with rate-limiting (max 3 attempts per 10 minutes) to prevent SMS bombing and brute-force attacks.
* **Technician Authentication:** Mobile / Employee ID + PIN bound to the physical device UUID. If a device is reported lost or an employee is terminated, changing status to `INACTIVE` immediately revokes their Firebase session tokens.
* **Admin Web Authentication:** Corporate Email + Password enforced with **Multi-Factor Authentication (MFA)** and automated session timeout after 30 minutes of inactivity.

---

# 4. Data Protection, Encryption & Privacy

### 4.1 Data in Transit
* All API calls, Firestore streams, and Cloud Storage uploads require **TLS 1.3 (HTTPS / WSS)** with HSTS enabled.
* Plaintext HTTP connections are automatically rejected at the Cloudflare / Firebase Edge CDN.

### 4.2 Data at Rest
* **Cloud Firestore:** Encrypted at rest using standard **AES-256** encryption managed by Google Cloud Key Management Service (KMS).
* **Cloud Storage:** Customer photos, signed job sheets, and PDF invoices are stored encrypted with strict access control.
* **Technician SQLite Database (Room):** Sensitive local offline queues and session tokens are encrypted on-device using Android Keystore and SQLCipher.

### 4.3 Personally Identifiable Information (PII) Redaction
* Customer phone numbers are masked when viewed in general reporting dashboards.
* Exact customer home addresses are hidden from technicians until the job status transitions to `TECHNICIAN_ACCEPTED` or `ON_THE_WAY`.

---

# 5. Server-Side Logic & Anti-Tampering Safeguards

To prevent client-side parameter tampering (e.g., modifying service rates, applying invalid coupon discounts, or skipping workflow steps):

1. **Server-Calculated Billing:** The client application transmits only `{ serviceId, configurationId, couponCode }`. The Cloud Function `calculateCartPricing` fetches verified base rates from `/services` and calculates totals on the server.
2. **Strict State Machine Transitions:** Bookings cannot transition to illegal states (e.g., `CONFIRMED` $\rightarrow$ `SERVICE_COMPLETED` without technician check-in). Transitions are guarded by transactional Cloud Functions.
3. **Database Security Rules:** Direct client write access to `/invoices`, `/pricing_rules`, and `/audit_logs` is set to `allow write: if false;`, ensuring modifications occur solely via the Admin SDK inside verified Cloud Functions.

---

# 6. Offline Data Security on Field Devices

Because the Technician Android App is offline-first:

1. **Encrypted Local Storage:** Offline job data, service checklists, and customer signatures are cached in a sandboxed Room database encrypted with keys stored in the **Android Keystore System**.
2. **Cryptographic Payload Signing:** Every offline event (`ARRIVED`, `MATERIALS_LOGGED`, `COMPLETED`) is stamped with a monotonic device timestamp and cryptographically hashed before being added to the sync queue.
3. **Media Sandbox:** Photos taken via CameraX are written directly to the application-private directory (`Context.getExternalFilesDir()`) and deleted from the local cache immediately upon successful Cloud Storage sync.

---

# 7. Payment Gateway & Financial Security

1. **PCI-DSS Compliance:** The platform does not store or process raw credit/debit card numbers, CVVs, or banking credentials. All payments use tokenized gateway SDKs (Razorpay / Stripe / Cashfree).
2. **Webhook Signature Verification:** Payment confirmation webhooks require HMAC-SHA256 signature verification matching the gateway secret before updating any booking status.
3. **Idempotency Safeguards:** Every payment event is checked against an immutable `payment_events/{webhookId}` collection to guarantee transactions cannot be double-credited or replayed.

---

# 8. Audit Logging & Non-Repudiation

An immutable, append-only audit trail (`/audit_logs`) records all administrative and operational actions:

* Price adjustments, discount/coupon creation, and tax rule updates.
* Manual booking status overrides and technician reassignments.
* Expense approvals and agency commission modifications.
* Account deactivations and permission changes.

Each audit record captures: `timestamp`, `actorId`, `actorRole`, `action`, `entityType`, `entityId`, `oldValue`, `newValue`, and `ipAddress`.

---

# 9. Infrastructure Security & App Integrity

* **Firebase App Check:** Integrated with **Google Play Integrity API** on Android and **reCAPTCHA Enterprise** on Web to block unauthorized API scrapers, bots, and modified APKs from calling backend functions.
* **CORS Policies:** Cloud Functions strictly enforce Cross-Origin Resource Sharing (CORS) whitelisting only the official Admin Web domain.
* **DDoS & WAF Protection:** Cloudflare Edge and Google Cloud Armor provide automated Layer 3/4 and Layer 7 distributed denial-of-service mitigation.

---

# 10. Incident Response & Security SLAs

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

*For security inquiries, audit requests, or vulnerability disclosures, contact the security team.*
