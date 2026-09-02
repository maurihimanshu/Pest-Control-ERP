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

## User Deactivation & Active Status

Firebase token validity does NOT determine ERP access. When a user's `is_active` field in PostgreSQL is set to `FALSE`:
1. The FirebaseAuthenticationFilter still validates the token signature
2. After loading the user record from PostgreSQL, the filter checks `is_active`
3. If `is_active = FALSE`, the filter returns HTTP 401 regardless of token validity
4. Firebase token revocation is a separate identity-management concern
5. There is no race window where a deactivated user can access the ERP (unlike token-only approaches which require waiting for token expiry)

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

## Agency/Tenant Scope Enforcement

Every authenticated user has an agency_id loaded from PostgreSQL (for non-CUSTOMER, non-SUPER_ADMIN roles). This is extracted in the FirebaseAuthenticationFilter and stored in the SecurityContext. Service layer methods extract agency_id from the authentication principal and include it in all queries for agency-scoped resources. Agents cannot access another agency's resources by modifying the URL.

See `docs/RBAC_AND_PERMISSIONS.md` for the canonical permissions matrix.
See `docs/ARCHITECTURE.md` for the full authentication/authorization flow.

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

---

## 6. Technician Device Lifecycle & Local Data Security

### 6.1 Technician Device Identity & Registration Lifecycle
To prevent unauthorized offline replay attacks and credential sharing:
1. **Device Enrollment:** When a Field Technician signs in, the app transmits the physical hardware UUID to `POST /api/v1/auth/device/register`.
2. **Single Active Device Policy:** The platform enforces a strict single active device per technician constraint. Registering a replacement phone automatically revokes the previous device registration.
3. **Lost Device / Instant Revocation:** If a phone is lost or compromised, an Agency Manager or Admin marks the device `REVOKED` in the Admin ERP, which immediately blocks all sync endpoints (`POST /api/v1/dispatch/visits/sync`) and triggers a remote wipe command.

### 6.2 SQLCipher & Android Keystore Key Lifecycle
1. **Hardware-Backed Master Key:** The Technician Mobile App generates a 256-bit AES cipher key stored exclusively in the **Android Keystore System** (`AndroidKeyStore` provider).
2. **Local Room Encryption:** SQLite databases are encrypted at rest using SQLCipher with the Keystore master key.
3. **Automated Local Wipe:**
   - On explicit technician logout: All cached offline visit data and session tokens are purged from Room.
   - On remote session revocation / tampering detection (Play Integrity failure): The app executes a complete local database file destruction.

### 6.3 Hardware-Backed Device Payload Signing (P0-02)
To secure offline operations against replay and payload tampering:
1. **Keystore Keypair:** Upon device registration, the Technician App generates an **EC P-256 Keypair** in the Android Keystore with `KeyGenParameterSpec.Builder(KeyProperties.PURPOSE_SIGN)`.
2. **Device Signature Header:** For critical mutations (`START_VISIT`, `COMPLETE_VISIT`, `LOG_CHEMICALS`), the device signs the normalized JSON body and attaches `X-Device-Signature: <base64-signature>` along with `X-Device-Id: <device-uuid>`.
3. **Server Verification:** `OfflineSyncController` validates the cryptographic signature using the technician's registered public key prior to executing database mutations.

---

## 7. Multi-Tenant Defense-in-Depth via PostgreSQL RLS (P0-03)

In addition to Spring Security filter checks and repository query scoping:
1. **Session Scope Binding:** For each authenticated HTTP request, a Spring Security interceptor / Hibernate connection hook sets PostgreSQL session parameters:
   ```sql
   SET LOCAL app.current_agency_id = '<agency-uuid>';
   SET LOCAL app.is_super_admin = 'false';
   ```
2. **PostgreSQL RLS Enforcement:** Tables like `work_orders`, `service_visits`, `sync_conflicts`, and `inventory_transactions` enforce Row Level Security, preventing accidental cross-tenant data leakage even in the event of an application-layer query bug.

---

*Governed by Spring Security 6 standards, Android Keystore hardware security, and enterprise identity protocols.*

