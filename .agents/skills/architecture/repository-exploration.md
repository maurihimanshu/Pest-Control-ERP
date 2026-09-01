---
name: repository-exploration
description: Systematically explores the repository layout and module structure before executing tasks.
category: architecture
triggers:
  - explore repo
  - find files
  - understand structure
inputs:
  - target directory
outputs:
  - directory structure map
dependencies:
  - architecture-rules
related_skills:
  - architecture-discovery
---

# Skill: Repository Exploration

## Purpose
To ensure agents have a correct, updated mental model of the codebase before making changes.

## When to Use
- When first joining the project or conversation.
- Before proposing new files or modules.
- When searching for where a specific feature resides.

## When NOT to Use
- If the exact file path is already known and verified.

## Required Context
- Understanding of the Modular Monolith structure (com.pestcontrol.modules.*).

## Step-by-Step Workflow
1. List root directories to identify build tools (Maven `pom.xml` or Gradle `build.gradle`).
2. Search for the main Spring Boot application class to locate the base package.
3. List the contents of `src/main/java/**/modules/` to identify existing domain modules.
4. Check `src/main/resources/` for configuration files (`application.yml`) and database migrations (e.g., Flyway `db/migration`).
5. Map out the standard layered architecture within a target module (controller, service, repository, entity, dto).

## Validation Checklist
- [ ] Confirmed the location of the base package.
- [ ] Identified active domain modules.
- [ ] Located the database migration scripts.

## Common Mistakes
- Assuming standard monolithic structure without verifying modular boundaries.
- Editing files in the wrong module due to name similarities.
