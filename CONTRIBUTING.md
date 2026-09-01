# Contributing Guide & Engineering Standards
## Pest Control Enterprise Resource Planning (ERP) Platform

Thank you for contributing to the **Pest Control ERP Platform**! This guide sets out the development workflow, coding standards, branch conventions, and testing requirements across our multi-platform codebase:
* **Backend Core:** Java 21 + Spring Boot 3.3.x (Maven)
* **Customer Android Application:** Java 21
* **Technician Android Application:** Java 21 (Offline-First)
* **Web Admin ERP Dashboard:** React 18 + TypeScript

---

## Table of Contents

1. [Core Engineering Principles](#1-core-engineering-principles)
2. [Local Development Environment Setup](#2-local-development-environment-setup)
3. [Git Branching Strategy & Workflow](#3-git-branching-strategy--workflow)
4. [Platform-Specific Coding Standards](#4-platform-specific-coding-standards)
   - [4.1 Backend (Java 21 / Spring Boot / Maven)](#41-backend-java-21--spring-boot--maven)
   - [4.2 Android Applications (Customer & Technician)](#42-android-applications-customer--technician)
   - [4.3 Admin Web Dashboard (React + TypeScript)](#43-admin-web-dashboard-react--typescript)
5. [Commit Message Conventions](#5-commit-message-conventions)
6. [Pull Request (PR) Process & Checklist](#6-pull-request-pr-process--checklist)
7. [Security, Secrets & Environment Hygiene](#7-security-secrets--environment-hygiene)

---

# 1. Core Engineering Principles

1. **Zero-Trust Client Access:** Never calculate prices, discounts, or state transitions on the client side. Business rules must be verified in Spring Boot domain services.
2. **Offline-Resilient Field Operations:** Any feature added to the Technician App must gracefully handle network disconnection and queue operations in SQLite (Room DB) via Android `WorkManager`.
3. **Clean Code & Strong Typing:** Write self-documenting code with strict types (no `any` in TypeScript; strong DTOs and immutable records in Java 21).
4. **Test-Driven Reliability:** All business-critical logic (pricing engine, state transitions, Flyway migrations) must include unit tests (JUnit 5 / Mockito) and integration tests (Testcontainers).

---

# 2. Local Development Environment Setup

### Required Tooling:
* **Java Development Kit (JDK):** Version **21** (Eclipse Temurin / OpenJDK 21).
* **Build Tool:** Apache Maven **3.9+**.
* **Android Studio:** Ladybug (2024.2+) or later with Android SDK 34/35.
* **Node.js & Package Manager:** Node.js **20 LTS** and `npm` / `pnpm`.
* **Docker & Docker Compose:** For running local PostgreSQL 16, Redis 7, and RabbitMQ 3.13 instances.
* **Git:** Configured with your official work email and GPG commit signing.

### Local Infrastructure Bootstrapping:
```bash
# 1. Clone the repository
git clone https://github.com/maurihimanshu/Pest-Control-ERP.git
cd Pest-Control-ERP

# 2. Start local PostgreSQL, Redis, and RabbitMQ via Docker Compose
docker compose -f infrastructure/docker-compose.local.yml up -d

# 3. Build & run the Spring Boot backend
cd backend
mvn clean spring-boot:run

# 4. Build & run the Web Admin ERP
cd ../admin-web
npm install
npm run dev
```

---

# 3. Git Branching Strategy & Workflow

We follow **Git Flow** with strict branch protection rules on `main` and `staging`:

```text
  main (Production releases only)
   ▲
   │ (Release Tag & Hotfixes)
  staging (Pre-production UAT & Integration)
   ▲
   │ (Merged via PR)
  feature/  or  bugfix/  or  hotfix/
```

### Branch Naming Conventions:
* `feature/<module>-<short-description>` (e.g., `feature/dispatch-gantt-board`, `feature/inventory-batch-expiry`)
* `bugfix/<module>-<issue-description>` (e.g., `bugfix/pricing-coupon-tax-rounding`, `bugfix/tech-app-gps-timeout`)
* `hotfix/<critical-patch>` (e.g., `hotfix/payment-webhook-duplicate-ack`)

---

# 4. Platform-Specific Coding Standards

## 4.1 Backend (Java 21 / Spring Boot / Maven)

* **Architecture:** Modular Monolith with package-by-feature (`com.pestcontrol.modules.<module>`).
* **Database Migrations:** Every database schema change must be a new Flyway migration script under `src/main/resources/db/migration/V{N}__{description}.sql`. Never modify existing migration scripts.
* **Entities & Repositories:** Use Spring Data JPA. Explicitly define fetch types (`FetchType.LAZY` for `@ManyToOne` and `@OneToMany`).
* **DTOs & Records:** Use Java 21 `record` or immutable POJOs for request and response DTOs.
* **Input Validation:** Annotate all request DTOs with Jakarta Bean Validation (`@NotNull`, `@NotBlank`, `@Size`, `@Min`).
* **Formatting:** Run `mvn spotless:apply` or `mvn checkstyle:check` prior to opening a PR.

---

## 4.2 Android Applications (Customer & Technician)

* **Architecture:** MVVM (Model-View-ViewModel) + Repository Pattern + Clean Domain Use Cases.
* **Build System:** Gradle with **Kotlin DSL (`build.gradle.kts`)**.
* **Target & Compile SDK:** Compile SDK 34/35, Min SDK 24 (Android 7.0+).
* **Dependency Injection:** Hilt / Dagger for all view models and repositories.
* **UI & Views:** ViewBinding / Jetpack Compose; zero `findViewById()` usage.
* **Resources:**
  * **Zero Hardcoded Strings:** All text must be defined in `res/values/strings.xml`.
  * **Dimensions & Colors:** Use centralized design tokens in `res/values/colors.xml` and `dimens.xml`.
* **Offline Sync in Technician App:**
  * Use **Room Database** for all local entity tables.
  * Background synchronization must strictly utilize **Android `WorkManager`** with exponential backoff and network constraints.
  * Images captured with CameraX must be compressed to $< 500\text{ KB}$ WebP before queueing.

---

## 4.3 Admin Web Dashboard (React + TypeScript)

* **Language:** TypeScript with **`strict: true`** enabled in `tsconfig.json`. The `any` type is strictly forbidden.
* **Styling:** TailwindCSS + Ant Design / Shadcn UI components.
* **State Management:**
  * Server State: React Query / TanStack Query.
  * Global Client State: Zustand or Redux Toolkit.
* **Formatting & Linting:** Code must pass ESLint and Prettier without warnings prior to commit:
  ```bash
  npm run lint
  npm run format:check
  ```

---

# 5. Commit Message Conventions

We adhere to the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <short imperative description>

[optional body]

[optional footer(s)]
```

### Allowed Types:
* `feat`: A new user-facing feature.
* `fix`: A bug fix.
* `refactor`: Code change that neither fixes a bug nor adds a feature.
* `perf`: A code change that improves performance.
* `docs`: Documentation changes only.
* `style`: Formatting, missing semi-colons, whitespace changes.
* `test`: Adding missing tests or correcting existing tests.
* `chore`: Build scripts, CI/CD configuration, package dependencies.

### Examples:
```text
feat(bookings): implement 3-tier work order auto-generation
fix(pricing): correct tax calculation on partial coupon discount
refactor(tech-app): migrate local photo queue to Room DB with SQLCipher
docs(api): update OpenAPI contract for offline visit sync endpoint
```

---

# 6. Pull Request (PR) Process & Checklist

1. **Keep PRs Focused:** Limit PRs to a single feature or bugfix ($< 400$ lines of diff preferred).
2. **Sync with Base:** Always rebase your feature branch onto the latest `staging` before opening a PR.
3. **PR Description:** Fill out the PR template completely (summary of changes, linked ticket, testing steps, screenshots).
4. **Automated Checks:** All CI/CD pipelines (Testcontainers, linting, build checks) must be green.
5. **Code Reviews:** Requires at least **1 approving review** from a Lead/Senior developer before merge.

---

# 7. Security, Secrets & Environment Hygiene

> [!CAUTION]
> **NEVER commit sensitive credentials, API keys, or private configuration files to Git.**

### Prohibited from Version Control (`.gitignore` enforced):
* `application-prod.yml` / production database passwords
* `google-services.json` (Production Android keys)
* `service-account-key.json` (Firebase Admin SDK private keys)
* `.env`, `.env.local`, `.env.production`
* Keystores (`*.jks`, `*.keystore`) and signing password properties
* Local SQLite / Room test databases

---

*Thank you for adhering to our engineering standards and maintaining high software quality!*
