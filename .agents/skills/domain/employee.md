---
name: employee
description: Managing employees, technicians, and their skill sets.
category: domain
triggers:
  - Onboard technician
  - Manage technician skills
  - Agency roster
inputs:
  - Employee details
outputs:
  - Employee service implementation
dependencies:
  - database/postgresql-schema
related_skills:
  - domain/dispatch
---

# Skill: Employee Domain

## Purpose
To manage internal staff, specifically field technicians, their assigned agencies (franchises), certifications, and skill sets for accurate dispatch matching.

## When to Use / When NOT to Use
**Use When:** Onboarding staff, managing Role-Based Access Control (RBAC) data, or querying available skills for a job.
**NOT to Use:** For customer management.

## Required Context
Technicians are the core operational asset. Their skills dictate which `Work Orders` they can be assigned to.

## Domain Rules & Constraints
1. **Roles:** Employees have specific roles (ADMIN, DISPATCHER, TECHNICIAN, MANAGER).
2. **Agency Association:** Most technicians belong to a specific `agency_id` (branch). Cross-branch dispatching requires special overrides.
3. **Skills Matrix:** A many-to-many relationship (`employee_skills`) tracks what services a tech is qualified to perform (e.g., Termite Control requires specific certification).

## Entity Structure
*   `employees`: `id`, `firebase_uid`, `full_name`, `phone`, `role`, `agency_id`, `is_active`
*   `skills`: `id`, `name`, `description`
*   `employee_skills`: `employee_id`, `skill_id`, `certified_until`

## Spring Service Methods
*   `Employee onboardTechnician(OnboardTechDto dto)`
*   `void assignSkill(UUID employeeId, UUID skillId, LocalDate expiry)`
*   `List<Employee> findAvailableTechsBySkill(UUID skillId, LocalDate date, UUID agencyId)`

## API Endpoints
*   `POST /api/v1/employees`
*   `GET /api/v1/employees/{id}`
*   `GET /api/v1/employees/technicians?skillId={id}`

## Database Considerations
*   Foreign key `agency_id` must be indexed.
*   Join table `employee_skills` needs composite primary key `(employee_id, skill_id)`.

## RabbitMQ Events
*   `TechnicianOnboardedEvent`

## Validation Checklist
- [ ] Are skills properly modeled as a many-to-many relationship?
- [ ] Are roles clearly defined and enforced in API security?
- [ ] Is agency isolation possible for multi-tenant franchise setups?

## Common Mistakes
*   Hardcoding skills as boolean columns in the `employees` table (e.g., `can_do_termites`, `can_do_rodents`).
*   Allowing technicians to register themselves via public APIs.

## Related Skills
- `domain/dispatch`
- `security/rbac`
