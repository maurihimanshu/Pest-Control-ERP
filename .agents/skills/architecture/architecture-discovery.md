---
name: architecture-discovery
description: Discovers and validates the implemented architecture against the canonical rules using code analysis.
category: architecture
triggers:
  - validate architecture
  - check compliance
  - analyze codebase
inputs:
  - module name
outputs:
  - compliance report
dependencies:
  - architecture-rules
related_skills:
  - legacy-architecture-audit
---

# Skill: Architecture Discovery

## Purpose
To verify that the actual code conforms to the documented architecture (Spring Boot, Postgres, etc.) and hasn't drifted.

## When to Use
- When auditing a module.
- Before approving a large PR or feature branch.
- When generating architecture documentation.

## When NOT to Use
- For simple bug fixes where architecture isn't impacted.

## Required Context
- `_architecture_rules.md`

## Step-by-Step Workflow
1. **Database Check**: Grep for `@Entity`, `JpaRepository`, and flyway SQL scripts to ensure PostgreSQL usage.
2. **Caching Check**: Grep for `@Cacheable`, `RedisTemplate` to ensure Redis is used correctly.
3. **Event Check**: Grep for `RabbitTemplate`, `@RabbitListener` to confirm RabbitMQ usage.
4. **API Check**: Validate that controllers are RESTful (`@RestController`).
5. **Security Check**: Check for Spring Security configurations and absence of client-side authority logic.

## Validation Checklist
- [ ] No Firestore imports (`com.google.cloud.firestore`).
- [ ] No Cloud Functions imports.
- [ ] Only JPA/Hibernate used for persistent domain entities.
- [ ] Module boundaries respected (no direct repository calls across modules).

## Common Mistakes
- Relying on outdated documentation instead of checking actual imports.
- Missing cross-module coupling where one module injects another's repository directly.
