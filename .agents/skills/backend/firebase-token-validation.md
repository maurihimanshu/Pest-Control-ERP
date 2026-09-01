---
name: firebase-token-validation
description: Implements Firebase ID token validation in Spring Security.
category: backend
triggers:
  - configure auth
  - validate firebase token
inputs:
  - SecurityFilterChain config
outputs:
  - Authentication filter and provider
dependencies:
  - architecture-rules
related_skills:
  - spring-boot-module
---

# Skill: Firebase Token Validation

## Purpose
To securely authenticate requests using Firebase Auth (the chosen identity provider) while mapping users to the internal PostgreSQL domain.

## Rules & Constraints
1. **Never** store Firebase logic deeply in domain services. Confine it to the `auth` module and Spring Security filters.
2. The client passes the Firebase JWT in the `Authorization: Bearer <token>` header.
3. The backend validates the signature using the Firebase Admin SDK.
4. The backend then extracts the `uid`, looks up the corresponding `User` entity in PostgreSQL, and creates a Spring Security `Authentication` object.

## Step-by-Step Workflow
1. Add Firebase Admin SDK dependency.
2. Initialize `FirebaseApp` using service account credentials.
3. Create a `FirebaseTokenFilter` extending `OncePerRequestFilter`.
4. Inside `doFilterInternal`, extract the Bearer token.
5. Call `FirebaseAuth.getInstance().verifyIdToken(token)`.
6. Extract `uid` and email.
7. Load user from database or create dynamically (if auto-provisioning).
8. Set `SecurityContextHolder.getContext().setAuthentication(...)`.

## Validation Checklist
- [ ] Token is verified offline via Google public keys (handled by SDK).
- [ ] User context is fully populated in Spring Security.
- [ ] Expired tokens are rejected gracefully (401 Unauthorized).

## Common Mistakes
- Hitting the Firebase REST API directly instead of using the Admin SDK, which causes severe latency.
- Trusting client-sent roles instead of loading RBAC roles from PostgreSQL.
