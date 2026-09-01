---
name: pricing
description: Managing dynamic pricing rules, tiers, and coupon validation.
category: domain
triggers:
  - Calculate booking price
  - Apply coupon
  - Manage area-based pricing
inputs:
  - Service selection
  - Location details
outputs:
  - Calculated price
dependencies:
  - domain/booking
related_skills:
  - database/postgresql-schema
---

# Skill: Pricing Domain

## Purpose
To accurately calculate the cost of services dynamically based on property size, location, selected add-ons, taxes, and promotional coupons.

## When to Use / When NOT to Use
**Use When:** A customer is building their cart, or an admin is creating a manual booking.
**NOT to Use:** For post-job invoice generation (which just reads the stored price) unless a formal change order is requested.

## Required Context
**NEVER TRUST CLIENT-SIDE PRICING.** The mobile app or web frontend may display estimated prices, but the final calculation MUST happen on the server before `CONFIRMING` a booking.

## Domain Rules & Constraints
1. **Server-Side Authority:** The `PricingService` is the sole authority on price.
2. **Calculation Formula:** `Base Price (based on Area/BHK) + Add-ons - Coupon Discount + Taxes = Final Price`.
3. **Coupons:** Must have expiration dates, usage limits, and condition checks (e.g., valid only for first-time users or specific services).

## Entity Structure
*   `services`: `id`, `name`, `base_price`
*   `pricing_rules`: `id`, `service_id`, `rule_type` (BHK, SQFT), `multiplier`
*   `coupons`: `id`, `code`, `discount_type` (PERCENTAGE, FLAT), `value`, `max_discount`, `valid_until`, `usage_limit`

## Spring Service Methods
*   `PricingResult calculatePrice(PricingRequestDto request)`
*   `CouponValidationResult validateCoupon(String code, UUID customerId, BigDecimal subtotal)`

## API Endpoints
*   `POST /api/v1/pricing/calculate`
*   `POST /api/v1/pricing/validate-coupon`

## Database Considerations
*   Keep pricing rules flexible, perhaps using JSONB for complex condition matrices if standard relational columns become too restrictive.
*   Track coupon usage in a separate table to enforce `usage_limit`.

## RabbitMQ Events
*   None typically, this is a synchronous calculation domain.

## Validation Checklist
- [ ] Is the calculation strictly server-side?
- [ ] Are coupons validated against expiration, limits, and applicability?
- [ ] Does the formula correctly apply discounts before calculating tax (usually required by law)?

## Common Mistakes
*   Accepting `total_amount` from a client API request and saving it directly to the database.
*   Hardcoding prices in code instead of a database-driven rules engine.

## Related Skills
- `domain/booking`
