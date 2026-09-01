# Offline-First Architecture & Synchronization Specification
## Technician Field Android Application & Spring Boot API

**Document Version:** 1.0.0  
**Client Stack:** Android Native (Java 21) + Room Database + WorkManager + CameraX  
**Backend Stack:** Spring Boot 3.3.x + PostgreSQL 16  
**Date:** September 2026  

---

## 1. Offline-First Philosophy & Design Goals

Pest control technicians operate in basements, industrial warehouses, sub-ground tunnels, and remote agricultural sites where cellular connectivity is intermittent or absent.

### Architecture Goals:
1. **100% Core Field Operability Offline:** Technicians must be able to view assigned daily schedules, inspect premises, log chemical dosages, take before/after photos, and capture customer sign-offs without an active network connection.
2. **Deterministic Background Sync:** All offline mutations are staged in a local SQLite (Room) transactional queue and dispatched via Android `WorkManager` upon network recovery.
3. **Idempotency & Zero Duplicate Mutations:** Every local event carries a client-generated UUID `idempotencyKey` and monotonic sequence number.
4. **Deterministic Conflict Resolution:** Explicit, rule-based conflict handling ensures field physical evidence is never silently discarded.

### Security without Cryptographic Payload Signing (V1):
Offline operations are secured through:
- Firebase JWT authentication (user identity cryptographically verified by Firebase)
- operation_id UUID idempotency (prevents replay of individual operations)
- device_id registration (device linked to employee account in PostgreSQL)
- local_sequence ordering (operations processed in correct order)
- Server-side state validation (backend is authoritative — stale client operations rejected)
- Complete audit trail in audit_logs

Cryptographic payload signing (e.g., Android Keystore Ed25519 signatures on each operation payload) is documented in ADR-006 as a future security hardening option for Phase 2.

---

## 2. Technician Mobile Offline Architecture

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      Technician Android Application                    │
 │                                                                        │
 │  ┌────────────────────────┐         ┌───────────────────────────────┐  │
 │  │      Presentation      │         │           CameraX             │  │
 │  │  (Activities/Fragments)│         │ (Hardware Capture & Compressor│  │
 │  └───────────┬────────────┘         └───────────────┬───────────────┘  │
 │              │ User Actions                         │ Photo Saved      │
 │              ▼                                      ▼                  │
 │  ┌──────────────────────────────────────────────────────────────────┐  │
 │  │                     Repository & Domain Layer                    │  │
 │  └──────────────────────────────────┬───────────────────────────────┘  │
 │                                     │                                  │
 │         ┌───────────────────────────┴───────────────────────────┐      │
 │         ▼                                                       ▼      │
 │  ┌──────────────────────────────┐              ┌────────────────────┐  │
 │  │      Local SQLite Database   │              │ Sandboxed Storage  │  │
 │  │     (Room DB + SQLCipher)    │              │  (WebP < 500 KB)   │  │
 │  │ • cached_visits              │              └─────────┬──────────┘  │
 │  │ • cached_chemicals           │                        │             │
 │  │ • offline_action_queue       │                        │             │
 │  └──────────────┬───────────────┘                        │             │
 │                 │ Staged Actions                         │             │
 │                 ▼                                        ▼             │
 │  ┌──────────────────────────────────────────────────────────────────┐  │
 │  │                 Android WorkManager (Background Sync)            │  │
 │  │   Constraint: NetworkCapabilities.NET_CAPABILITY_INTERNET        │  │
 │  └──────────────────────────────────┬───────────────────────────────┘  │
 └─────────────────────────────────────┼──────────────────────────────────┘
                                       │ HTTPS / REST (Multipart / Batch)
                                       ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                        Spring Boot Backend API                         │
 │                                                                        │
 │              POST /api/v1/dispatch/visits/sync                         │
 │  • Validates Idempotency Keys                                          │
 │  • Executes Conflict Resolution Rules                                  │
 │  • Uploads Photos to Object Storage                                    │
 │  • Updates PostgreSQL System-of-Record in Atomic Transaction           │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Local Action Queue (Room Database Schema)

When the technician executes an action offline, it is written immediately to `offline_action_queue`:

```text
Operation Queue Fields:
- operation_id UUID (primary key for idempotency — generated on device)
- device_id VARCHAR (registered device, linked to employee in PostgreSQL)
- event_id UUID (same as operation_id for atomically-created operations)
- local_sequence BIGINT (monotonically increasing per device — for ordering)
- client_created_at TIMESTAMPTZ (device clock — informational only, NOT authoritative timestamp)
- server_received_at TIMESTAMPTZ (set by server — authoritative timestamp)
- operation_type VARCHAR (VISIT_ARRIVED, VISIT_STARTED, MATERIALS_LOGGED, VISIT_COMPLETED, PHOTO_UPLOADED)
- payload JSONB
- payload_version INT (for schema evolution)
- retry_count INT
- sync_status VARCHAR (PENDING, SYNCING, SYNCED, FAILED, CONFLICT)
- last_sync_error TEXT
```

---

## 4. Conflict Handling & Resolution Matrix

When the mobile app synchronizes with the server, conflicts between offline actions and concurrent online administrative changes are resolved via deterministic rules:

### Conflict Resolution Policy

**Principle:** Offline synchronization must NEVER silently override a newer authoritative administrative or financial decision.

| Conflict Scenario | Default Behavior | Authorization Required | Audit |
|:---|:---|:---|:---|
| Offline COMPLETED arrives after admin CANCELLED | Create conflict record, notify DISPATCHER/AGENCY_MANAGER, DO NOT override cancellation | DISPATCHER or ADMIN to resolve | audit_logs + conflict_record |
| Offline COMPLETED with chemical usage after batch marked expired | Reject chemical deduction, flag for supervisor review | AGENCY_MANAGER to approve retroactive adjustment | audit_logs |
| Offline COMPLETED after technician reassignment | Create conflict record, original technician's completion flagged | DISPATCHER to attribute credit | audit_logs |
| Duplicate operation_id submitted | Return previously computed result, no re-processing | None | idempotency log |

**Conflict Record:**
```sql
-- Stored as a support_ticket type 'SYNC_CONFLICT' or separate conflict_records table
-- Contains: original_server_state, submitted_offline_payload, conflict_type, created_at, resolved_at, resolved_by, resolution
```

---

## 5. Media Staging & Local Compression

1. **CameraX Capture:** Photos captured in field inspection are passed directly to an in-memory bitmap pipeline.
2. **Local Compression:** Resized to a maximum resolution of $1920 \times 1080$ and compressed using **WebP (quality 80%)**, yielding files under $400\text{ KB}$ (a $>85\%$ reduction compared to raw camera JPEGs).
3. **Multipart Upload:** When network connectivity is established, photos are uploaded directly to the Object Storage signed URL before the completion JSON payload is submitted.

---

*Governed by offline-first mobile engineering principles and idempotent backend API standards.*
