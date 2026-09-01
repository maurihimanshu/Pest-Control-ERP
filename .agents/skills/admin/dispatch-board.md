---
name: admin-dispatch-board
description: Skill for Admin dispatch board React component.
category: admin
triggers:
  - build dispatch board
inputs:
  - work orders
  - technicians
outputs:
  - react components
dependencies: []
related_skills:
  - admin-booking-management
---

# admin-dispatch-board

## Purpose
Skill for Admin dispatch board React component. Cover: work order list, technician availability calendar, drag-and-drop assignment, POST /api/v1/dispatch/work-orders/{id}/assign, real-time update strategy.

## When to Use
Building the dispatch board in the React admin app.

## When NOT to Use
For non-admin interfaces.

## Required Context
- React, Ant Design

## Inputs
- UI Requirements

## Expected Outputs
- Dispatch board component

## Rules & Constraints
1. Must use strictly REST APIs for fetching data.
2. Drag and drop must be optimistic but revert on failure.

## Step-by-Step Workflow
1. Fetch work orders and availability.
2. Render calendar and list.
3. Implement DnD context.
4. Call assign API on drop.

## Validation Checklist
- [ ] API integration works.
- [ ] Optimistic updates handle errors properly.

## Common Mistakes
- Polling too frequently (consider WebSockets for real-time, or reasonable interval polling).

## Example Usage
```tsx
// DispatchBoard component
```

## Related Skills
- admin-booking-management

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
