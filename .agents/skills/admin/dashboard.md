---
name: admin-dashboard
description: Skill for Admin dashboard.
category: admin
triggers:
  - build dashboard
inputs:
  - metrics api
outputs:
  - dashboard components
dependencies: []
related_skills:
  - admin-reporting
---

# admin-dashboard

## Purpose
Skill for Admin dashboard. Cover: KPI cards (bookings today, revenue, active technicians), charts (Recharts), API polling vs WebSocket strategy, loading states, error states.

## When to Use
Building the main landing page for the admin panel.

## When NOT to Use
For detailed data manipulation (use lists/forms instead).

## Required Context
- KPI endpoints

## Inputs
- Dashboard layout specs

## Expected Outputs
- Responsive KPI dashboard

## Rules & Constraints
1. KPI APIs must be optimized (e.g. cached via Redis).
2. UI must handle loading and error states gracefully.

## Step-by-Step Workflow
1. Fetch metrics from `/api/v1/metrics/dashboard`.
2. Display KPI summary cards.
3. Use Recharts to render trend lines.
4. Implement periodic polling (e.g., 60s) or WebSockets.

## Validation Checklist
- [ ] Dashboards load under 2 seconds.
- [ ] Charts handle empty data correctly.

## Common Mistakes
- Running heavy COUNT() queries on PostgreSQL on every dashboard load.

## Example Usage
```tsx
// KPI Card
```

## Related Skills
- admin-reporting

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
