# ADR-015: V1 Security and Data-Integrity Hardening

**Status:** Accepted  
**Date:** September 2026  
**Deciders:** Principal Architect, Product Owner  
**Supersedes:** ADR-006, ADR-009 (only the decisions identified below)  
**Superseded by:** None  
**Related:** ADR-002, ADR-008, docs/AUTHENTICATION_AND_AUTHORIZATION.md, docs/CONCURRENCY_AND_IDEMPOTENCY.md, docs/DATABASE_DESIGN.md  
**Affected Artifacts:** offline sync, authorization, schema, testing, agent rules

## Context

The pre-implementation security review identified two unacceptable V1 risks: offline field mutations were not cryptographically bound to a registered device, and agency isolation depended solely on application query discipline. The review also established that complete, migration-ready schema contracts are required before implementation.

## Decision

1. Critical offline mutations (`START_VISIT`, `COMPLETE_VISIT`, `LOG_CHEMICALS`) require an EC P-256 Android Keystore signature over a canonical operation envelope. The backend verifies it against a registered, active `technician_devices` public key before any state mutation.
2. The system remains a single-company, shared-schema application partitioned by `agency_id`. PostgreSQL RLS is mandatory defense-in-depth for every agency-scoped table. The runtime database role is non-owner, does not have `BYPASSRLS`, and policies are forced on protected tables. Application-level `agency_id` filtering remains mandatory.
3. Agency-owned operational and financial records are immutable in ownership: their `agency_id` is `NOT NULL` and agencies are deactivated, never hard-deleted.
4. Financial JSON values use decimal strings; PostgreSQL sequences guarantee unique, monotonic allocation, not gapless numbering.

## Consequences

### Positive

- Offline evidence is bound to an enrolled device and is tamper-evident.
- A missed application filter cannot expose another agency's data.
- The implementation has one authoritative schema contract for ledgers, devices, and supporting module tables.

### Negative / Trade-offs

- Device key registration, canonical serialization, RLS migration tests, and a non-owner runtime database role are required from the first vertical slice.
- Invoice numbers can contain auditable gaps; no code may promise gapless numbering.

## Status History

- September 2026: Accepted following pre-implementation review.
