---
name: impact-analysis
description: Assesses the impact of a proposed change across all layers of the modular monolith.
category: architecture
triggers:
  - analyze impact
  - what breaks if
inputs:
  - proposed change description
  - target classes
outputs:
  - impact report
dependencies:
  - repository-exploration
related_skills:
  - module-boundary-validation
---

# Skill: Impact Analysis

## Purpose
To prevent unintended side-effects by systematically tracing dependencies before applying a change.

## When to Use
- Before modifying a shared module (e.g., `core`, `auth`).
- Before changing database schemas.
- Before modifying public service interfaces.

## Step-by-Step Workflow
1. **Identify the Core Change**: Determine the exact class/interface/table being changed.
2. **Trace Upwards (Dependents)**: Use `grep` to find all usages of the class/interface across other modules.
3. **Trace Downwards (Dependencies)**: Identify what the changed class depends on, to ensure no transitive issues.
4. **Database Impact**: If changing an entity, assess the need for Flyway migrations.
5. **API Impact**: If changing a controller/DTO, assess client app (Android/React) impact.
6. **Event Impact**: If changing RabbitMQ events, assess consumer impact.

## Validation Checklist
- [ ] Checked for cross-module usage.
- [ ] Assessed database migration needs.
- [ ] Assessed API contract breakage.

## Common Mistakes
- Only checking the local module and missing dependent modules.
- Forgetting to check test files for breakages.
