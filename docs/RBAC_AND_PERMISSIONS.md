# RBAC & Permissions Reference
Implementation Status: Documentation / Architecture Baseline
— Backend: Not implemented
— Customer Android: Not implemented
— Technician Android: Not implemented
— Admin Web: Not implemented

This document is the single authoritative source for all roles, permissions, and tenant-scoping rules.

## 1. System Roles (7 Defined Roles)

- **SUPER_ADMIN**: Full system access across all agencies, full data access, audit log access.
- **ADMIN**: Full operational access across all agencies. Cannot modify system configuration or audit logs.
- **ACCOUNTANT**: Financial read/write (payments, invoices, expenses, reports). Cannot dispatch or manage services.
- **DISPATCHER**: Booking management, technician assignment, work orders, scheduling. Cannot access financial data.
- **AGENCY_MANAGER**: Branch-scoped access to their own agency's technicians, inventory, expenses, reports, and bookings.
- **TECHNICIAN**: Own job queue only. Read access to service catalog. Cannot access other technicians' data or financials.
- **CUSTOMER**: Own bookings, payments, invoices, profile, and AMC contracts. Read access to service catalog/pricing.

## 2. Permissions Matrix

| Resource | SUPER_ADMIN / ADMIN | ACCOUNTANT | DISPATCHER | AGENCY_MANAGER | TECHNICIAN | CUSTOMER |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Service Catalog** | Create/Update/Delete | Read | Read | Read | Read | Read |
| **Pricing Rules** | Create/Update/Delete | Read | Read | Read | Read | Read |
| **Customers** | All | Read | All | Branch Scoped | Read (job scope) | Own Profile |
| **Employees** | All | Read | All | Branch Scoped | Own Profile | None |
| **Bookings** | All | Read | All | Branch Scoped | Read (job scope) | Own Bookings |
| **Work Orders** | All | Read | All | Branch Scoped | Own Assigned | None |
| **Service Visits**| All | Read | All | Branch Scoped | Own Assigned | None |
| **Payments** | All | All | None | Read (Branch) | None | Own (Read) |
| **Invoices** | All | All | None | Read (Branch) | None | Own (Read) |
| **Inventory** | All | Read | None | Branch Stock | Own Trunk | None |
| **Expenses** | All | All | None | Branch Scoped | None | None |
| **Reports** | All | All | None | Branch Scoped | None | None |
| **AMC Contracts** | All | Read | All | Branch Scoped | Read (job scope) | Own (Read) |
| **Support Tickets**| All | None | Read | Branch Scoped | Own | Own |
| **Audit Logs** | SUPER_ADMIN only| None | None | None | None | None |
| **User Mgmt** | All | None | None | Branch Scoped | Own Profile | Own Profile |

## 3. Tenant & Agency Scope Rules

- **AGENCY_MANAGER**: Can only access resources where `agency_id = [their_agency_id]`.
- **TECHNICIAN**: Can only access `work_orders`/`service_visits` where `primary_employee_id = [their_employee_id]`.
- **CUSTOMER**: Can only access resources where `customer_id = [their_customer_id]`.
- **DISPATCHER**: In a multi-agency configuration, restricted to assigning technicians and viewing bookings within their specific agency (or globally if using a single-company configuration). *Configuration choice applies globally via application properties.*
- **ADMIN / SUPER_ADMIN**: Cross-agency access permitted.

## 4. Object-Level Authorization Rules

- URL manipulation (e.g., changing `booking_id`, `agency_id`, or `employee_id` in paths) MUST NOT bypass ownership checks.
- All resource ownership is verified in `@PreAuthorize` constraints or directly within the Service layer.
- Resource ownership is NEVER assumed purely from the URL path.

**Spring Security Implementation Example**:
```java
@PreAuthorize("hasRole('ADMIN') or (hasRole('CUSTOMER') and @bookingAuthz.isOwner(#bookingId, authentication))")
@GetMapping("/{bookingId}")
public BookingResponse getBooking(@PathVariable UUID bookingId) {
    // ...
}
```

## 5. User Deactivation Flow

Token validity at the identity provider (Firebase) is secondary to the system database. 
- If a user is deactivated (`is_active = false` in PostgreSQL), the backend `FirebaseAuthenticationFilter` or custom `UserDetailsService` MUST reject ALL requests with HTTP 401/403.
- This ensures immediate revocation without waiting for the 1-hour Firebase JWT expiration.
