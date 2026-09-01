---
name: admin-booking-management
description: Skill for Admin booking management.
category: admin
triggers:
  - build booking management
inputs:
  - bookings api
outputs:
  - react lists and forms
dependencies: []
related_skills:
  - admin-dispatch-board
---

# admin-booking-management

## Purpose
Skill for Admin booking management. Cover: booking list with filters/pagination, booking detail view, status management, cancel, reschedule, manual assignment actions. Must call backend APIs — never direct DB access.

## When to Use
Building booking management views in the Admin panel.

## When NOT to Use
For customer-facing views.

## Required Context
- Ant Design tables

## Inputs
- Booking domain model

## Expected Outputs
- Booking list and details views

## Rules & Constraints
1. No direct database access. Use `/api/v1/bookings`.
2. Implement server-side pagination and filtering.

## Step-by-Step Workflow
1. Build table with server-side pagination.
2. Add filters (status, date range).
3. Build detail view for actioning (cancel, reschedule).

## Validation Checklist
- [ ] Server-side pagination is wired up.
- [ ] Actions map to correct REST endpoints.

## Common Mistakes
- Fetching all bookings and paginating on the client.

## Example Usage
```tsx
// BookingList component
```

## Related Skills
- admin-dispatch-board

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
