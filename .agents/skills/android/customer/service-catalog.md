---
name: customer-service-catalog
description: Skill for Customer Android service catalog.
category: android
triggers:
  - implement service catalog
inputs:
  - service catalog endpoints
outputs:
  - catalog ui
  - caching logic
dependencies: []
related_skills:
  - customer-booking-flow
---

# customer-service-catalog

## Purpose
Skill for Customer Android service catalog. Cover: fetching from /api/v1/services, caching, search, filtering, detail screen.

## When to Use
When building the service listing and details UI in the customer app.

## When NOT to Use
For technician viewing their assigned services.

## Required Context
- Backend service endpoints

## Inputs
- UI Requirements

## Expected Outputs
- Cached catalog list

## Rules & Constraints
1. Fetch from `/api/v1/services`.
2. Cache the list locally to improve performance.
3. Allow searching and filtering.

## Step-by-Step Workflow
1. Create Retrofit interface.
2. Fetch and store in Room or DataStore for caching.
3. Bind to RecyclerView.
4. Implement filter/search locally on the cached list.

## Validation Checklist
- [ ] Catalog loads quickly.
- [ ] Offline viewing works if previously cached.
- [ ] Search filtering is accurate.

## Common Mistakes
- Not caching, resulting in slow load times.

## Example Usage
```java
// Fetch catalog
```

## Related Skills
- customer-booking-flow

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
