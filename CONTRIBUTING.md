# Contributing Guide & Engineering Standards
## Pest Control Enterprise Resource Planning (ERP) Platform

Thank you for contributing to the **Pest Control ERP Platform**! This guide sets out the development workflow, coding standards, branch conventions, and testing requirements across our multi-platform codebase:
* **Customer Android Application** (Java 21)
* **Technician Android Application** (Java 21, Offline-First)
* **Web Admin ERP Dashboard** (React 18 + TypeScript)
* **Firebase Backend & Cloud Functions** (TypeScript, Node.js 20)

---

## Table of Contents

1. [Core Engineering Principles](#1-core-engineering-principles)
2. [Local Development Environment Setup](#2-local-development-environment-setup)
3. [Git Branching Strategy & Workflow](#3-git-branching-strategy--workflow)
4. [Platform-Specific Coding Standards](#4-platform-specific-coding-standards)
   - [4.1 Android Applications (Customer & Technician)](#41-android-applications-customer--technician)
   - [4.2 Admin Web Dashboard (React + TypeScript)](#42-admin-web-dashboard-react--typescript)
   - [4.3 Cloud Functions & Backend (TypeScript)](#43-cloud-functions--backend-typescript)
5. [Commit Message Conventions](#5-commit-message-conventions)
6. [Pull Request (PR) Process & Checklist](#6-pull-request-pr-process--checklist)
7. [Security, Secrets & Environment Hygiene](#7-security-secrets--environment-hygiene)

---

# 1. Core Engineering Principles

1. **Zero-Trust Client Access:** Never calculate prices, discounts, or state transitions on the client side. Business rules must be verified in Firebase Cloud Functions.
2. **Offline-Resilient Field Operations:** Any feature added to the Technician App must gracefully handle network disconnection and queue operations in SQLite (Room DB) via Android `WorkManager`.
3. **Clean Code & Strong Typing:** Write self-documenting code with strict types (no `any` in TypeScript; strong object models and immutable DTOs in Java).
4. **Test Coverage:** All business-critical logic (pricing engine, state transitions, security rules) must include unit and integration tests.

---

# 2. Local Development Environment Setup

### Required Tooling:
* **Java Development Kit (JDK):** Version **21** (Temurin / OpenJDK).
* **Android Studio:** Ladybug (2024.2+) or later with Android SDK 34/35.
* **Node.js & Package Manager:** Node.js **20 LTS** and `npm` / `pnpm`.
* **Firebase CLI:** Install globally via `npm install -g firebase-tools`.
* **Git:** Configured with your official work email and GPG commit signing (recommended).

### Initial Setup:
```bash
# 1. Clone the repository
git clone https://github.com/your-org/pest-control-erp.git
cd pest-control-erp

# 2. Install Firebase tools & login
firebase login

# 3. Setup Web Admin dependencies (when initialized)
cd admin-web && npm install

# 4. Setup Cloud Functions dependencies (when initialized)
cd ../functions && npm install
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
* `feature/<component>-<short-description>` (e.g., `feature/tech-app-camera-compression`, `feature/admin-dispatch-gantt`)
* `bugfix/<component>-<issue-description>` (e.g., `bugfix/functions-coupon-rounding`, `bugfix/cust-app-otp-timeout`)
* `hotfix/<critical-patch>` (e.g., `hotfix/payment-webhook-race-condition`)

---

# 4. Platform-Specific Coding Standards

## 4.1 Android Applications (Customer & Technician)

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

## 4.2 Admin Web Dashboard (React + TypeScript)

* **Language:** TypeScript with **`strict: true`** enabled in `tsconfig.json`. The `any` type is strictly forbidden.
* **Styling:** TailwindCSS + Ant Design / Shadcn UI components.
* **State Management:**
  * Server State: React Query / TanStack Query (or Firebase onSnapshot hooks).
  * Global Client State: Zustand or Redux Toolkit.
* **Formatting & Linting:** Code must pass ESLint and Prettier without warnings prior to commit:
  ```bash
  npm run lint
  npm run format:check
  ```

---

## 4.3 Cloud Functions & Backend (TypeScript)

* **Runtime:** Node.js 20 on Cloud Functions (v2).
* **Input Validation:** Every callable Cloud Function must validate arguments using schema validators (e.g., **Zod**).
* **Transactional Integrity:** Any booking status progression or inventory decrement must run inside a **Firestore Transaction** (`db.runTransaction()`).
* **Error Handling:** Use `HttpsError` with appropriate error codes (`unauthenticated`, `permission-denied`, `invalid-argument`, `failed-precondition`).
* **Security Rules Testing:** Changes to `firestore.rules` or `storage.rules` must be verified using the Firebase Local Emulator Suite:
  ```bash
  firebase emulators:start --only firestore,functions
  npm test
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
feat(cust-app): implement Google Maps pin address selection
fix(functions): prevent double-invocation on payment webhook retry
refactor(tech-app): migrate local photo cache to WebP compressor
docs(srs): update state machine transition table for reschedule flow
```

---

# 6. Pull Request (PR) Process & Checklist

1. **Keep PRs Focused:** Limit PRs to a single feature or bugfix ($< 400$ lines of diff preferred).
2. **Sync with Base:** Always rebase your feature branch onto the latest `staging` before opening a PR.
3. **PR Description:** Fill out the PR template completely:
   * Summary of changes.
   * Linked issue/ticket number (e.g., `Closes #124`).
   * Screenshots / video recordings for UI changes.
   * Steps to manually test the changes.
4. **Automated Checks:** All CI/CD pipelines (linting, static analysis, unit tests) must be green.
5. **Code Reviews:** Requires at least **1 approving review** from a Lead/Senior developer before merge.

---

# 7. Security, Secrets & Environment Hygiene

> [!CAUTION]
> **NEVER commit sensitive credentials, API keys, or private configuration files to Git.**

### Prohibited from Version Control (`.gitignore` enforced):
* `google-services.json` (Production Android keys)
* `service-account-key.json` (Firebase Admin SDK private keys)
* `.env`, `.env.local`, `.env.production`
* Keystores (`*.jks`, `*.keystore`) and signing password properties
* Local SQLite / Room test databases

Use `.env.example` templates to document required environment variables without committing actual secrets.

---

*Thank you for adhering to our engineering standards and maintaining high software quality!*
