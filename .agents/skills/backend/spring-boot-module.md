---
name: spring-boot-module
description: Creates a new standard Spring Boot domain module with correct layered architecture.
category: backend
triggers:
  - create module
  - new domain module
inputs:
  - module name
outputs:
  - directory structure and base classes
dependencies:
  - architecture-rules
related_skills:
  - rest-controller
  - service-layer
  - repository-layer
---

# Skill: Spring Boot Module Creation

## Purpose
To scaffold a new domain module in the Modular Monolith ensuring consistent package structure and architectural layering.

## Rules & Constraints
1. Module must reside under `com.pestcontrol.modules.{domain}`.
2. Must include standard sub-packages: `web`, `service`, `repository`, `domain`, `dto`.

## Step-by-Step Workflow
1. Create the base directory: `src/main/java/com/pestcontrol/modules/{domain}`.
2. Create sub-packages:
   - `domain`: JPA `@Entity` classes and value objects.
   - `repository`: Spring Data `JpaRepository` interfaces.
   - `service`: Business logic interfaces and `@Service` implementations.
   - `web`: `@RestController` classes.
   - `dto`: Request and Response records/classes.
3. Define the public API (Service interface) that other modules are allowed to use.
4. Ensure the module is component-scanned by the main application class.

## Validation Checklist
- [ ] Directory structure matches canonical layout.
- [ ] No cyclic dependencies introduced.

## Common Mistakes
- Creating a separate `pom.xml` or `build.gradle` (we are using a single build file with logical modularity via packages in V1, unless multi-module build is explicitly configured).
