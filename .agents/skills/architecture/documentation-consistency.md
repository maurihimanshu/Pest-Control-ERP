---
name: documentation-consistency
description: Audits project documentation to ensure it reflects the current canonical architecture.
category: architecture
triggers:
  - audit docs
  - check doc consistency
inputs:
  - docs directory
outputs:
  - documentation audit report
dependencies:
  - architecture-rules
related_skills:
  - legacy-architecture-audit
---

# Skill: Documentation Consistency

## Purpose
To ensure all readmes, ADRs, and wiki pages align with the canonical Spring Boot + PostgreSQL architecture and don't mislead developers with obsolete information.

## When to Use
- After major architectural decisions.
- When generating or updating the primary `README.md`.
- As a periodic cleanup task.

## Rules & Constraints
- Documentation MUST state that PostgreSQL is the System of Record.
- Documentation MUST NOT propose Firestore/Firebase for domain data.

## Step-by-Step Workflow
1. Search `.md` files for outdated keywords (`firestore`, `cloud functions`, `nosql for erp`).
2. Identify conflicting architectural diagrams or text.
3. Generate a list of files that need updates.
4. (Optional) Propose exact textual replacements using the `architecture-rules` as the source of truth.

## Validation Checklist
- [ ] README.md reflects current stack.
- [ ] Onboarding docs point to Spring Boot, not legacy systems.

## Common Mistakes
- Leaving old setup instructions (e.g., `npm install -g firebase-tools` for backend deployments) in the backend readme.
