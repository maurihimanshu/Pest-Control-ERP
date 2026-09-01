---
name: admin-reporting
description: Skill for Admin reporting screens.
category: admin
triggers:
  - build reporting
inputs:
  - report endpoints
outputs:
  - report tables
  - export functions
dependencies: []
related_skills:
  - admin-dashboard
---

# admin-reporting

## Purpose
Skill for Admin reporting screens. Cover: paginated report tables, async CSV/Excel export (POST request + polling download), date range filters, branch filters.

## When to Use
Building data-heavy reports for accountants or managers.

## When NOT to Use
For simple CRUD views.

## Required Context
- Complex SQL queries

## Inputs
- Reporting requirements

## Expected Outputs
- Filterable tables and exports

## Rules & Constraints
1. Large exports must be async (create job, poll for file URL).
2. Paginated views must use offset or keyset pagination properly.

## Step-by-Step Workflow
1. Provide UI for date ranges and filters.
2. Fetch paginated preview.
3. Trigger export job via POST.
4. Poll status and download CSV/Excel.

## Validation Checklist
- [ ] Exports don't timeout the API.
- [ ] Filters apply correctly.

## Common Mistakes
- Trying to download a 100k row CSV synchronously.

## Example Usage
```tsx
// Export button logic
```

## Related Skills
- admin-dashboard

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
