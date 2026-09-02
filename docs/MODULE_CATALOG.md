# Canonical Module Catalog & Architecture Registry
**Architecture Baseline:** 2026.09 (V2.1.0)  
**Document Version:** 2.1.0  
**Pattern:** Spring Boot 3.x Modular Monolith (Single Deployable Artifact)  
**Package Base:** `com.pestcontrol.modules.*`  
**System of Record:** PostgreSQL 16  
**Date:** September 2026  

---

## 1. Architectural Guardrails & Module Boundary Rules

1. **Monolithic Deployment, Modular Design:** The entire system is built and deployed as a single Java 21 Spring Boot JAR artifact comprising 18 strictly bounded domain modules under `com.pestcontrol.modules.*`.
2. **Subdomains vs. Modules:**
   - **`catalog`:** Implements both the Service Catalog and Dynamic Pricing subdomains. There is NO separate `pricing` Java module.
   - **`payments`:** Implements payment gateway orchestration, COD reconciliation, and sequential PDF Invoicing in V1. There is NO separate `invoices` Java module.
   - **`employees`:** Implements the `Employee` aggregate. Technicians, Dispatchers, and Agency Managers are roles within the Employee identity model, NOT separate entities.
3. **Tenancy Identifier Standard:** All agency-scoped entities and APIs strictly use **`agency_id`** (never `tenant_id`).
4. **No Cross-Module Repository Access:** A module may NEVER inject or reference another module's `@Repository`, `@Entity`, or internal database tables directly.
5. **Public Service Interfaces:** Synchronous cross-module communication is strictly conducted through exported public Java service interfaces located in `com.pestcontrol.modules.<module_name>.api.*`.
6. **Asynchronous Decoupling via Outbox & RabbitMQ:** Cross-module asynchronous reactions are driven by domain events persisted transactionally into `outbox_events` and published via RabbitMQ.
7. **No Circular Dependencies:** The dependency graph between modules must be a Directed Acyclic Graph (DAG). Circular package imports are strictly prohibited.

---

## 2. Canonical 18 Domain Modules

```text
com.pestcontrol.modules.
├── auth          # 1. Identity & Security Filter Chain
├── users         # 2. User Accounts & RBAC Roles
├── customers     # 3. Customer Profiles & Addresses
├── employees     # 4. Technicians & Staff Skills Matrix
├── agencies      # 5. Branches, Territories & Commissions
├── catalog       # 6. Service Catalog & Dynamic Pricing
├── bookings      # 7. Commercial Bookings & Slot Capacity
├── dispatch      # 8. Work Orders, Service Visits & Field Sync
├── payments      # 9. Gateways, Webhooks, Invoices & COD
├── inventory     # 10. Chemicals, Batches, Warehouses & COGS
├── expenses      # 11. Branch Operating Expenses & Fuel Logs
├── amc           # 12. Annual Maintenance Contracts
├── notifications # 13. Multi-Channel Alert Dispatch (FCM/SMS/Email)
├── support       # 14. Support Tickets, Complaints & Ratings
├── files         # 15. Presigned Object Storage Management
├── reporting     # 16. Analytics, KPI Aggregations & Exports
├── audit         # 17. Immutable Append-Only Audit Logging
└── outbox        # 18. Transactional Outbox Engine & Broker Relay
```

---

## 3. Module Specifications Matrix

### 1. `auth`
* **Package:** `com.pestcontrol.modules.auth`
* **Responsibility:** Firebase ID token cryptographic validation, custom claims extraction, stateless Spring Security session filters, and security context initialization.
* **Owned Tables:** None (Stateless authentication layer).
* **Public Service API:** `AuthService`, `TokenValidationService`
* **Emitted Events:** `UserAuthenticatedEvent`
* **Consumed Events:** None
* **Permitted Dependencies:** `users`, `audit`
* **Forbidden Dependencies:** `bookings`, `dispatch`, `payments`, `inventory`, `catalog`

### 2. `users`
* **Package:** `com.pestcontrol.modules.users`
* **Responsibility:** User accounts, credentials metadata, user status (`active`, `deactivated`), and role mappings (`CUSTOMER`, `TECHNICIAN`, `AGENCY_MANAGER`, `DISPATCHER`, `ACCOUNTANT`, `ADMIN`, `SUPER_ADMIN`).
* **Owned Tables:** `users`, `roles`, `user_roles`
* **Public Service API:** `UserQueryService`, `UserManagementService`
* **Emitted Events:** `UserCreated`, `UserDeactivated`, `UserRoleAssigned`
* **Consumed Events:** None
* **Permitted Dependencies:** `audit`
* **Forbidden Dependencies:** `bookings`, `dispatch`, `payments`, `inventory`

### 3. `customers`
* **Package:** `com.pestcontrol.modules.customers`
* **Responsibility:** Customer profiles (commercial/residential), property addresses with GPS coordinates, GST registrations, and customer communication preferences.
* **Owned Tables:** `customers`, `customer_addresses`
* **Public Service API:** `CustomerQueryService`, `CustomerProfileService`, `CustomerAddressService`
* **Emitted Events:** `CustomerRegistered`, `CustomerAddressAdded`
* **Consumed Events:** `UserCreated`
* **Permitted Dependencies:** `users`, `audit`
* **Forbidden Dependencies:** `bookings`, `dispatch`, `inventory`, `payments`

### 4. `employees`
* **Package:** `com.pestcontrol.modules.employees`
* **Responsibility:** Field technician profiles, skills/certification matrix, employee codes, agency association, ratings, and working shifts.
* **Owned Tables:** `employees`, `skills`, `employee_skills`
* **Public Service API:** `EmployeeQueryService`, `TechnicianSkillService`, `ShiftManagementService`
* **Emitted Events:** `EmployeeCreated`, `EmployeeSkillUpdated`, `EmployeeDeactivated`
* **Consumed Events:** `UserCreated`
* **Permitted Dependencies:** `users`, `agencies`, `audit`
* **Forbidden Dependencies:** `bookings`, `payments`, `inventory`

### 5. `agencies`
* **Package:** `com.pestcontrol.modules.agencies`
* **Responsibility:** Multi-tenant branch and franchise management, assigned postal/pincode territories, operational settings, and commission structures.
* **Owned Tables:** `agencies`, `agency_service_areas`
* **Public Service API:** `AgencyQueryService`, `AgencyManagementService`, `TerritoryLookupService`
* **Emitted Events:** `AgencyCreated`, `AgencyTerritoryUpdated`
* **Consumed Events:** None
* **Permitted Dependencies:** `audit`
* **Forbidden Dependencies:** `bookings`, `dispatch`, `payments`, `inventory`

### 6. `catalog`
* **Package:** `com.pestcontrol.modules.catalog`
* **Responsibility:** Service categories, individual services, treatment packages, warranty durations, and dynamic pricing rules (BHK, square footage, pest severity, add-ons).
* **Owned Tables:** `service_categories`, `services`, `pricing_rules`, `pricing_tiers`
* **Public Service API:** `CatalogQueryService`, `PricingCalculationService`, `ServiceManagementService`
* **Emitted Events:** `ServiceCatalogUpdated`, `PricingRuleModified`
* **Consumed Events:** None
* **Permitted Dependencies:** `audit`
* **Forbidden Dependencies:** `bookings`, `dispatch`, `payments`, `inventory`

### 7. `bookings`
* **Package:** `com.pestcontrol.modules.bookings`
* **Responsibility:** Commercial customer bookings, booking line items, coupons & redemptions, slot availability calendar queries, and transactional capacity pool reservations.
* **Owned Tables:** `bookings`, `booking_items`, `booking_events`, `coupons`, `coupon_redemptions`, `availability_slots`
* **Public Service API:** `BookingCreationService`, `BookingQueryService`, `CouponService`, `SlotReservationService`
* **Emitted Events:** `BookingCreated`, `BookingConfirmed`, `BookingCancelled`, `BookingRescheduled`, `BookingCompleted`, `BookingClosed`
* **Consumed Events:** `PaymentCompleted`, `PaymentRefunded`, `WorkOrderCompleted`, `AMCVisitGenerated`
* **Permitted Dependencies:** `customers`, `catalog`, `agencies`, `audit`, `outbox`
* **Forbidden Dependencies:** `dispatch` (direct repository/entity access), `payments` (direct repository/entity access)

### 8. `dispatch`
* **Package:** `com.pestcontrol.modules.dispatch`
* **Responsibility:** Operational dispatch management, owning both `work_orders` and `service_visits` (1:N cardinality), technician job assignment, dispatch board queries, field checklists, and technician offline queue synchronization.
* **Owned Tables:** `work_orders`, `service_visits`, `service_checklists`, `offline_sync_logs`
* **Public Service API:** `WorkOrderService`, `ServiceVisitService`, `DispatchAssignmentService`, `OfflineSyncService`
* **Emitted Events:** `WorkOrderCreated`, `TechnicianAssigned`, `TechnicianAccepted`, `TechnicianRejected`, `ServiceVisitStarted`, `ServiceVisitCompleted`, `ServiceVisitFailed`, `WorkOrderCompleted`
* **Consumed Events:** `BookingConfirmed`, `BookingCancelled`, `AMCVisitScheduled`
* **Permitted Dependencies:** `bookings`, `employees`, `agencies`, `inventory`, `audit`, `outbox`
* **Forbidden Dependencies:** `payments` (direct repository/entity access), `catalog`

### 9. `payments`
* **Package:** `com.pestcontrol.modules.payments`
* **Responsibility:** Payment transaction lifecycle, payment gateway integrations (Razorpay/Stripe), cryptographically signed webhook processing, webhook deduplication (`payment_events`), Cash on Delivery (COD) tracking, and automated sequential PDF invoice generation.
* **Owned Tables:** `payments`, `payment_events`, `payment_transactions`, `invoices`, `invoice_items`
* **Public Service API:** `PaymentProcessingService`, `WebhookHandlingService`, `InvoiceGenerationService`, `RefundService`
* **Emitted Events:** `PaymentInitiated`, `PaymentAuthorized`, `PaymentCompleted`, `PaymentFailed`, `PaymentRefunded`, `InvoiceGenerated`
* **Consumed Events:** `BookingCreated`, `BookingCancelled`, `ServiceVisitCompleted`
* **Permitted Dependencies:** `bookings`, `customers`, `files`, `audit`, `outbox`
* **Forbidden Dependencies:** `inventory`, `employees`, `dispatch` (direct repository/entity access)

### 10. `inventory`
* **Package:** `com.pestcontrol.modules.inventory`
* **Responsibility:** Chemical products, batch tracking with FIFO expiration dates, multi-location stock balances (Central Warehouse -> Branch Warehouse -> Technician Trunk), transactional service material deduction during visit completion, and Cost of Goods Sold (COGS) calculation.
* **Owned Tables:** `chemical_products`, `chemical_batches`, `inventory_locations`, `inventory_transactions`, `service_material_usage`
* **Public Service API:** `InventoryStockService`, `BatchTrackingService`, `MaterialConsumptionService`, `WarehouseTransferService`
* **Emitted Events:** `StockReceived`, `StockTransferred`, `LowStockAlert`, `BatchExpiredAlert`
* **Consumed Events:** `ServiceVisitCompleted` (for async downstream reporting and replenishment alerts; authoritative deduction is executed synchronously inside visit completion transaction)
* **Permitted Dependencies:** `agencies`, `employees`, `audit`, `outbox`
* **Forbidden Dependencies:** `bookings`, `payments`, `support`

### 11. `expenses`
* **Package:** `com.pestcontrol.modules.expenses`
* **Responsibility:** Branch and agency operational expenses (fuel, vehicle maintenance, safety equipment, local office overhead), expense categorization, receipt attachments, and approval workflows.
* **Owned Tables:** `expenses`, `expense_categories`
* **Public Service API:** `ExpenseManagementService`, `ExpenseQueryService`
* **Emitted Events:** `ExpenseRecorded`, `ExpenseApproved`
* **Consumed Events:** None
* **Permitted Dependencies:** `agencies`, `employees`, `files`, `audit`
* **Forbidden Dependencies:** `bookings`, `dispatch`, `catalog`

### 12. `amc`
* **Package:** `com.pestcontrol.modules.amc`
* **Responsibility:** Annual Maintenance Contract (AMC) agreements, contract terms, billing milestones, and automated recurring visit schedule generation via scheduled background jobs.
* **Owned Tables:** `amc_contracts`, `amc_schedules`
* **Public Service API:** `AMCContractService`, `AMCScheduleService`
* **Emitted Events:** `AMCContractCreated`, `AMCVisitGenerated`, `AMCContractTerminated`
* **Consumed Events:** `ServiceVisitCompleted`, `PaymentCompleted`
* **Permitted Dependencies:** `customers`, `catalog`, `bookings`, `dispatch`, `audit`, `outbox`
* **Forbidden Dependencies:** `inventory`, `expenses`

### 13. `notifications`
* **Package:** `com.pestcontrol.modules.notifications`
* **Responsibility:** Multi-channel notification delivery (Firebase Cloud Messaging push, Transactional SMS via MSG91/Twilio, HTML emails via SendGrid/Resend, and WhatsApp Business API) driven by asynchronous domain events.
* **Owned Tables:** `notifications`, `notification_templates`, `device_tokens`
* **Public Service API:** `NotificationDispatchService`, `DeviceRegistrationService`
* **Emitted Events:** `NotificationSent`, `NotificationDeliveryFailed`
* **Consumed Events:** `BookingConfirmed`, `BookingCancelled`, `TechnicianAssigned`, `ServiceVisitCompleted`, `PaymentCompleted`, `InvoiceGenerated`, `LowStockAlert`
* **Permitted Dependencies:** `users`, `audit`
* **Forbidden Dependencies:** `bookings`, `dispatch`, `payments`, `inventory` (Direct database/entity dependencies forbidden; reacts strictly to domain event payloads)

### 14. `support`
* **Package:** `com.pestcontrol.modules.support`
* **Responsibility:** Customer complaints, post-service ratings, low-rating auto-escalations, warranty revisit requests, and customer support ticket resolution threads.
* **Owned Tables:** `support_tickets`, `support_messages`, `service_ratings`
* **Public Service API:** `SupportTicketService`, `RatingFeedbackService`
* **Emitted Events:** `TicketCreated`, `TicketEscalated`, `WarrantyClaimApproved`
* **Consumed Events:** `ServiceVisitCompleted`
* **Permitted Dependencies:** `customers`, `bookings`, `dispatch`, `audit`, `outbox`
* **Forbidden Dependencies:** `inventory`, `pricing`

### 15. `files`
* **Package:** `com.pestcontrol.modules.files`
* **Responsibility:** Object storage metadata tracking, secure presigned upload/download URL generation, storage provider abstraction (AWS S3 / Google Cloud Storage / Local Storage), and checksum verification.
* **Owned Tables:** `file_metadata`
* **Public Service API:** `FileStorageService`, `PresignedUrlGenerator`
* **Emitted Events:** `FileUploaded`, `FileDeleted`
* **Consumed Events:** None
* **Permitted Dependencies:** `audit`
* **Forbidden Dependencies:** `bookings`, `dispatch`, `payments`

### 16. `reporting`
* **Package:** `com.pestcontrol.modules.reporting`
* **Responsibility:** Read-only analytical queries, executive dashboard KPI calculations, branch gross margin & P&L aggregations, technician utilization metrics, and asynchronous CSV/Excel report exports.
* **Owned Tables:** None (Executes read-only analytical queries or consumes materialized reporting views).
* **Public Service API:** `DashboardAnalyticsService`, `FinancialReportService`, `OperationalReportService`, `ReportExportService`
* **Emitted Events:** `ReportGenerated`
* **Consumed Events:** `DailyKpiRollupTrigger`
* **Permitted Dependencies:** `bookings`, `dispatch`, `payments`, `inventory`, `expenses`, `agencies`, `files`
* **Forbidden Dependencies:** Direct write operations on any business module

### 17. `audit`
* **Package:** `com.pestcontrol.modules.audit`
* **Responsibility:** Cross-cutting immutable append-only audit logging capturing actor ID, action type, entity identifier, previous state JSONB, and new state JSONB for all administrative and operational mutations.
* **Owned Tables:** `audit_logs`
* **Public Service API:** `AuditLogService`
* **Emitted Events:** None
* **Consumed Events:** None
* **Permitted Dependencies:** None (Foundation module; must not depend on any business domain module)
* **Forbidden Dependencies:** All business modules

### 18. `outbox`
* **Package:** `com.pestcontrol.modules.outbox`
* **Responsibility:** Transactional outbox event persistence within domain `@Transactional` boundaries, scheduled polling publisher (e.g. `SELECT ... FOR UPDATE SKIP LOCKED`), guaranteed at-least-once message dispatch to RabbitMQ exchanges, and publication state tracking.
* **Owned Tables:** `outbox_events`
* **Public Service API:** `OutboxEventRepository`, `OutboxPublisherService`
* **Emitted Events:** Relays all domain events to RabbitMQ
* **Consumed Events:** None
* **Permitted Dependencies:** None (Infrastructure messaging module)
* **Forbidden Dependencies:** All business modules

---

## 4. Cross-Module Interaction Matrix

| Calling Module | Permitted Synchronous Dependency (via Public API) | Permitted Asynchronous Integration (via Outbox/RabbitMQ) |
|:---|:---|:---|
| **`bookings`** | `customers`, `catalog`, `agencies`, `audit`, `outbox` | Receives: `PaymentCompleted`, `WorkOrderCompleted` |
| **`dispatch`** | `bookings`, `employees`, `agencies`, `inventory`, `audit`, `outbox` | Receives: `BookingConfirmed`, `BookingCancelled`, `AMCVisitScheduled` |
| **`payments`** | `bookings`, `customers`, `files`, `audit`, `outbox` | Receives: `BookingCreated`, `ServiceVisitCompleted` |
| **`inventory`**| `agencies`, `employees`, `audit`, `outbox` | Receives: `ServiceVisitCompleted` (for alerts/replenishment) |
| **`notifications`**| `users`, `audit` | Receives: All business domain events |
| **`amc`** | `customers`, `catalog`, `bookings`, `dispatch`, `audit`, `outbox` | Receives: `PaymentCompleted`, `ServiceVisitCompleted` |
| **`support`** | `customers`, `bookings`, `dispatch`, `audit`, `outbox` | Receives: `ServiceVisitCompleted` |
| **`reporting`**| Read-only access across domain query services | Receives: Scheduled cron rollup triggers |
