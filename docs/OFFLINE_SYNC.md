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

```java
@Entity(tableName = "offline_action_queue")
public class OfflineActionEntity {
    @PrimaryKey
    @NonNull
    public String actionId; // UUID generated on device

    public String visitId;
    public String actionType; // 'ARRIVE', 'START', 'LOG_MATERIALS', 'COMPLETE'
    public String payloadJson; // Serialized request parameters
    public long clientTimestamp; // Monotonic device timestamp
    public int retryCount;
    public String syncStatus; // 'PENDING', 'UPLOADING_MEDIA', 'SYNCED', 'FAILED'
    public String errorMessage;
}
```

---

## 4. Conflict Handling & Resolution Matrix

When the mobile app synchronizes with the server, conflicts between offline actions and concurrent online administrative changes are resolved via deterministic rules:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                Conflict Resolution Rules Matrix                                 │
├───────────────────────────────┬─────────────────────────┬──────────────────────┬─────────────────┤
│ Field Action (Offline)        │ Server State (Online)   │ Resolution Strategy  │ Final State     │
├───────────────────────────────┼─────────────────────────┼──────────────────────┼─────────────────┤
│ Technician marks `COMPLETED`  │ Admin marked `CANCELLED`│ Physical Overrule    │ Visit marked    │
│ with photos & chemicals       │ while tech was offline  │ Server accepts visit │ `COMPLETED`;    │
│                               │                         │ & logs audit dispute │ Admin notified  │
├───────────────────────────────┼─────────────────────────┼──────────────────────┼─────────────────┤
│ Technician marks `COMPLETED`  │ Work Order reassigned   │ Original Tech Credit │ Visit linked to │
│ on old device                 │ to another technician   │ Service recorded for │ original tech;  │
│                               │                         │ acting technician    │ 2nd tech aborted│
├───────────────────────────────┼─────────────────────────┼──────────────────────┼─────────────────┤
│ Technician logs chemical      │ Chemical batch expired  │ Accept with Warning  │ Usage recorded; │
│ usage from allocated batch    │ in server inventory     │ Inventory deducted;  │ Warning flagged │
│                               │                         │ Quality alert raised │ to Branch Mgr   │
├───────────────────────────────┼─────────────────────────┼──────────────────────┼─────────────────┤
│ Retried sync with identical   │ Already processed by    │ Idempotent Acknowledge│ HTTP 200 OK     │
│ `actionId` UUID               │ server on previous run  │ Returns cached result│ No duplicate op │
└───────────────────────────────┴─────────────────────────┴──────────────────────┴─────────────────┘
```

---

## 5. Media Staging & Local Compression

1. **CameraX Capture:** Photos captured in field inspection are passed directly to an in-memory bitmap pipeline.
2. **Local Compression:** Resized to a maximum resolution of $1920 \times 1080$ and compressed using **WebP (quality 80%)**, yielding files under $400\text{ KB}$ (a $>85\%$ reduction compared to raw camera JPEGs).
3. **Multipart Upload:** When network connectivity is established, photos are uploaded directly to the Object Storage signed URL before the completion JSON payload is submitted.

---

*Governed by offline-first mobile engineering principles and idempotent backend API standards.*
