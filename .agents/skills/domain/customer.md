---
name: customer
description: Managing customer profiles, registration, and addresses.
category: domain
triggers:
  - Register customer
  - Manage customer addresses
  - View customer history
inputs:
  - Customer data
outputs:
  - Customer service implementation
dependencies:
  - database/postgresql-schema
related_skills:
  - security/firebase-token-validation
---

# Skill: Customer Domain

## Purpose
To manage the primary users of the system who request and pay for pest control services. This includes their profile, contact details, and multiple service addresses.

## When to Use / When NOT to Use
**Use When:** Handling user registration (post-Firebase auth), address management, and aggregating customer history.
**NOT to Use:** For internal staff management (use Employee domain).

## Required Context
Authentication is handled by Firebase Auth. The backend `customers` table acts as the authorization and domain source of truth, linking the `firebase_uid` to our internal UUID.

## Domain Rules & Constraints
1. **Firebase Link:** The `customers` table must store the `firebase_uid` returned by the mobile app's login. This is the bridge between auth and domain.
2. **Multiple Addresses:** A customer can have multiple addresses (Home, Office, Parents' Home). Addresses must be a separate entity `customer_addresses`.
3. **Soft Deletes:** Do not hard delete customers to maintain referential integrity for past bookings. An `is_active` boolean or a `DELETED` status should be used.

## Entity Structure
*   `customers`: `id`, `firebase_uid` (UNIQUE), `full_name`, `phone_number` (UNIQUE), `email`, `is_active`
*   `customer_addresses`: `id`, `customer_id`, `label` (Home/Office), `street_address`, `city`, `state`, `zip_code`, `lat`, `lng`, `is_default`

## Spring Service Methods
*   `Customer registerOrGetCustomer(String firebaseUid, CustomerRegistrationDto dto)`
*   `Address addAddress(UUID customerId, AddressDto dto)`
*   `CustomerProfile getProfile(UUID customerId)`

## API Endpoints
*   `POST /api/v1/customers/register`
*   `GET /api/v1/customers/me`
*   `POST /api/v1/customers/me/addresses`

## Database Considerations
*   `firebase_uid` and `phone_number` must have `UNIQUE` constraints.
*   Addresses should be indexed by `customer_id` and potentially geohashed if proximity search is needed later.

## RabbitMQ Events
*   `CustomerRegisteredEvent` -> Trigger welcome email.

## Validation Checklist
- [ ] Is Firebase UID securely mapped?
- [ ] Are phone numbers normalized before saving?
- [ ] Is address management decoupled from the main profile?

## Common Mistakes
*   Using Firebase as the database (System-of-Record). Firebase is for Auth ONLY. PostgreSQL is the database.
*   Storing only one address per customer in the `customers` table.

## Related Skills
- `security/firebase-token-validation`
