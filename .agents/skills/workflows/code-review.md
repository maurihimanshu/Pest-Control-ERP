---
name: workflows-code-review
description: High-level orchestration skill for code review.
category: workflows
triggers:
  - review code
---

# workflows-code-review
## Purpose
High-level orchestration skill for code review. Steps: inspect diff, check architecture (no Firebase drift), check security (auth/authz), check business rules (state machines, pricing server-side), check DB (Flyway migration, safe ALTER), check idempotency, check tests, check observability, check docs. Report findings by severity: BLOCKER | MAJOR | MINOR | SUGGESTION.
## Expected Outputs
Review checklist.

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
