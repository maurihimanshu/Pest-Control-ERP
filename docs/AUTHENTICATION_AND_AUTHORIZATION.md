# Authentication & Authorization Specification
## Spring Security & Firebase Identity Architecture

**Document Version:** 1.0.0  
**Identity Provider (IdP):** Firebase Authentication  
**Backend Security Framework:** Spring Security 6.3.x  
**Authorization Mechanism:** Role-Based Access Control (RBAC) & PostgreSQL Authority Matrix  
**Date:** September 2026  

---

## 1. Authentication vs. Authorization Separation

A fundamental architectural principle of the Pest Control ERP platform is the strict separation between **Identity Verification (Authentication)** and **Permission Governance (Authorization)**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           1. Authentication (IdP)                           │
│                            Firebase Authentication                          │
│  • Customer: Phone Number + SMS OTP / Google Sign-In                        │
│  • Technician: Employee ID / Mobile + PIN (Bound to Device UUID)            │
│  • Admin: Corporate Email + Password + Multi-Factor Authentication (MFA)    │
│  • Emits: Cryptographically signed Firebase ID Token (JWT)                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Bearer <Firebase_ID_Token>
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           2. Authorization (Backend)                        │
│                         Spring Security & PostgreSQL                        │
│  • FirebaseTokenFilter validates signature via Firebase Admin SDK           │
│  • Resolves User UUID from PostgreSQL and loads assigned Roles/Authorities  │
│  • Evaluates endpoint security filters & @PreAuthorize annotations          │
│  • Protects core business data and domain resources                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Token Validation & Filter Pipeline

### 2.1 Filter Sequence in Spring Boot

```text
HTTP Request (with Authorization: Bearer <token>)
        │
        ▼
[ FirebaseAuthenticationFilter ]
        │ 1. Extract Bearer Token
        │ 2. FirebaseAuth.getInstance().verifyIdToken(token)
        │
        ├──► Invalid/Expired? ──► Send HTTP 401 Unauthorized
        │
        ▼ 3. Token Validated (Firebase UID extracted)
[ UserService.loadUserByFirebaseUid(uid) ]
        │ 4. Query PostgreSQL for User, Roles, and Agency scope
        │ 5. Construct UserPrincipal implements UserDetails
        │
        ▼ 6. SecurityContextHolder.getContext().setAuthentication(auth)
[ Spring Security FilterChain ]
        │ 7. Check URL pattern authorization
        │
        ▼ 8. Dispatch to @RestController
[ Method Security: @PreAuthorize ]
```

---

## 3. Role-Based Access Control (RBAC) Matrix

### 3.1 System Roles
* `SUPER_ADMIN`: Full system access, audit log viewer, financial configuration.
* `ADMIN`: Central operations manager, employee & service manager, dispute resolver.
* `DISPATCHER`: Operational desk managing scheduling, work orders, and technician assignments.
* `AGENCY_MANAGER`: Regional branch manager with scope limited to their specific `agency_id`.
* `ACCOUNTANT`: Financial manager access to invoices, expenses, payments, and P&L reports.
* `TECHNICIAN`: Field staff with access strictly restricted to assigned `service_visits`.
* `CUSTOMER`: Self-service portal restricted strictly to own bookings, addresses, and invoices.

---

### 3.2 Granular Permission Matrix

| Authority / Permission | CUSTOMER | TECHNICIAN | AGENCY_MGR | DISPATCHER | ACCOUNTANT | ADMIN | SUPER_ADMIN |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `CATALOG_READ` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `CATALOG_MANAGE` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `BOOKING_CREATE_SELF` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `BOOKING_CREATE_ANY` | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| `BOOKING_READ_OWN` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `BOOKING_READ_BRANCH` | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `BOOKING_READ_ALL` | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `DISPATCH_ASSIGN` | ❌ | ❌ | ✅ (Branch) | ✅ | ❌ | ✅ | ✅ |
| `VISIT_EXECUTE_ASSIGNED`| ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `INVENTORY_VIEW` | ❌ | ✅ (Trunk) | ✅ (Branch) | ❌ | ❌ | ✅ | ✅ |
| `INVENTORY_MANAGE` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `EXPENSE_LOG_BRANCH` | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `FINANCIAL_REPORT_READ` | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| `AUDIT_LOG_READ` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 4. Method-Level Security & Domain Scoping

In addition to endpoint-level URL security, domain services utilize SpEL expressions to enforce tenant/ownership boundaries:

```java
// Ensure customer can only access their own booking
@PreAuthorize("hasRole('ADMIN') or (hasRole('CUSTOMER') and #customerId == principal.id)")
public BookingResponse getCustomerBooking(UUID customerId, UUID bookingId) { ... }

// Ensure technician can only complete assigned visits
@PreAuthorize("hasRole('ADMIN') or (hasRole('TECHNICIAN') and @visitSecurity.isAssignedTechnician(#visitId, principal.id))")
public ServiceVisitResponse completeVisit(UUID visitId, CompleteVisitRequest request) { ... }
```

---

## 5. Session Invalidation & Account Revocation

* **Instant Session Revocation:** When an employee or customer account is deactivated in PostgreSQL (`users.is_active = false`), the `FirebaseAuthenticationFilter` rejects subsequent requests immediately, even if the client's Firebase JWT has not reached its 1-hour expiration.
* **Token Refresh Lifecycle:** Mobile clients automatically refresh Firebase tokens every 55 minutes using the Firebase Client SDK.

---

*Governed by Spring Security 6 standards and enterprise identity protocols.*
