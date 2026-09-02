# Database Design & PostgreSQL Schema Specification
## Pest Control Enterprise Resource Planning (ERP) Platform

**Document Version:** 2.0.0  
**Database Engine:** PostgreSQL 16.x  
**Migration Tool:** Flyway 10.x  
**Date:** September 2026  

> **Architecture Reference:** See `docs/ARCHITECTURE.md` for the canonical system architecture, `docs/DOMAIN_MODEL.md` for entity relationships and state machines, and `docs/CONCURRENCY_AND_IDEMPOTENCY.md` for transactional concurrency specifications.

---

## 1. Relational Database Overview

PostgreSQL 16 serves as the authoritative, transactional **System-of-Record (SoR)** for the Pest Control ERP platform.

### Core Data Integrity Principles:
1. **Strict Referential Integrity:** Foreign key constraints with explicit `ON DELETE RESTRICT` or `ON DELETE CASCADE` rules prevent orphaned records.
2. **ACID Transactions:** Financial entries (payments, invoices, expenses) and booking lifecycle updates are committed atomically within PostgreSQL database transactions.
3. **Decoupled 3-Tier Execution:** Clear separation between `bookings` (commercial contract), `work_orders` (operational dispatch), and `service_visits` (field execution).
4. **Binary Offloading:** Large files (photos, PDFs, signatures) are stored in Object Storage; PostgreSQL stores only metadata and storage URI pointers in the `file_metadata` table.

---

## 2. Entity-Relationship Overview

```text
 ┌───────────────┐        ┌───────────────┐        ┌───────────────┐
 │   customers   │───1:N──│   bookings    │───1:N─ │ booking_items │
 └───────┬───────┘        └───────┬───────┘        └───────────────┘
         │ 1:N                    │ 1:N
 ┌───────▼───────┐        ┌───────▼───────┐        ┌───────────────┐
 │customer_addrs │        │  work_orders  │───1:N──│service_visits │
 └───────────────┘        └───────┬───────┘        └───────┬───────┘
                                  │                        │ 1:N
 ┌───────────────┐                │ 1:N            ┌───────▼───────────────┐
 │   employees   │◄───────────────┘                │service_material_usage │
 └───────┬───────┘                                 └───────┬───────────────┘
         │ 1:N                                             │ N:1
 ┌───────▼───────┐                                 ┌───────▼───────────────┐
 │employee_skills│                                 │   chemical_batches    │
 └───────────────┘                                 └───────────────────────┘
```

---

## 3. Core Database Schemas & DDL Specifications

### 3.1 Authentication, Users & Stakeholders

```sql
-- Core User Account (Mapped to Firebase UID)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(32) UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX idx_users_phone ON users(phone_number);

-- Roles & Permissions
CREATE TABLE roles (
    id VARCHAR(50) PRIMARY KEY, -- 'SUPER_ADMIN', 'DISPATCHER', 'AGENCY_MANAGER', 'TECHNICIAN', 'CUSTOMER'
    description VARCHAR(255) NOT NULL
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id VARCHAR(50) NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Customers & Customer Addresses
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    customer_type VARCHAR(30) NOT NULL DEFAULT 'RESIDENTIAL', -- 'RESIDENTIAL', 'COMMERCIAL'
    company_name VARCHAR(200),
    gst_number VARCHAR(30),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    address_title VARCHAR(50) NOT NULL, -- 'Home', 'Main Warehouse', 'Office'
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(20) NOT NULL,
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    special_instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer_addresses_cust ON customer_addresses(customer_id);
```

---

### 3.2 Agencies, Employees & Skill Matrix

```sql
CREATE TABLE agencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(150),
    email VARCHAR(255),
    phone VARCHAR(32),
    commission_rate NUMERIC(5, 2) NOT NULL DEFAULT 0.00, -- e.g. 15.00%
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    agency_id UUID REFERENCES agencies(id) ON DELETE SET NULL,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    designation VARCHAR(100) NOT NULL,
    emergency_contact VARCHAR(32),
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    current_active_job_id UUID,
    rating_average NUMERIC(3, 2) NOT NULL DEFAULT 5.00,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skills (
    id VARCHAR(50) PRIMARY KEY, -- 'TERMITE_DRILL', 'GENERAL_FUMIGATION', 'BEDBUG_HEAT', 'RODENT_BAITING'
    title VARCHAR(150) NOT NULL
);

CREATE TABLE employee_skills (
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    skill_id VARCHAR(50) NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    certified_date DATE,
    PRIMARY KEY (employee_id, skill_id)
);
```

---

### 3.3 Service Catalog, Pricing Rules & Coupons

```sql
CREATE TABLE service_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(150) UNIQUE NOT NULL,
    description TEXT,
    display_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES service_categories(id) ON DELETE RESTRICT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    short_description VARCHAR(500),
    detailed_description TEXT,
    pricing_model VARCHAR(50) NOT NULL, -- 'FIXED', 'AREA_SQFT', 'CONFIGURATION_BHK', 'ROOM_COUNT'
    base_price NUMERIC(12, 2) NOT NULL,
    estimated_duration_minutes INT NOT NULL DEFAULT 60,
    warranty_days INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE service_required_skills (
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    skill_id VARCHAR(50) NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (service_id, skill_id)
);

CREATE TABLE pricing_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    tier_name VARCHAR(100) NOT NULL, -- '1 BHK', '2 BHK', 'Commercial Tier 1'
    unit_min NUMERIC(10, 2),
    unit_max NUMERIC(10, 2),
    unit_price NUMERIC(12, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE coupons (
    code VARCHAR(50) PRIMARY KEY,
    discount_type VARCHAR(20) NOT NULL, -- 'PERCENTAGE', 'FLAT_AMOUNT'
    discount_value NUMERIC(10, 2) NOT NULL,
    max_discount_amount NUMERIC(10, 2),
    min_booking_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE NOT NULL,
    usage_limit INT,
    usage_count INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```

---

### 3.4 3-Tier Booking, Work Orders & Field Execution

```sql
-- 1. Commercial Booking
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_number VARCHAR(50) UNIQUE NOT NULL, -- 'BK-2026-00001'
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    customer_address_id UUID NOT NULL REFERENCES customer_addresses(id) ON DELETE RESTRICT,
    agency_id UUID REFERENCES agencies(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'CONFIRMED', 'CANCELLED', 'CLOSED'
    payment_status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- PaymentStatus: PENDING, AUTHORIZED, PAID, PARTIAL, FAILED, REFUNDED, PARTIALLY_REFUNDED
    scheduled_date DATE NOT NULL,
    scheduled_time_slot VARCHAR(50) NOT NULL,
    subtotal_amount NUMERIC(12, 2) NOT NULL,
    discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    tax_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    total_payable_amount NUMERIC(12, 2) NOT NULL,
    coupon_code VARCHAR(50) REFERENCES coupons(code),
    customer_notes TEXT,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_cust ON bookings(customer_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_date ON bookings(scheduled_date);

CREATE TABLE booking_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    pricing_tier VARCHAR(100),
    quantity NUMERIC(10, 2) NOT NULL DEFAULT 1.00,
    unit_price NUMERIC(12, 2) NOT NULL,
    line_total NUMERIC(12, 2) NOT NULL
);

-- 2. Operational Work Order
CREATE TABLE work_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_order_number VARCHAR(50) UNIQUE NOT NULL, -- 'WO-2026-00001'
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    agency_id UUID REFERENCES agencies(id) ON DELETE SET NULL,
    order_type VARCHAR(50) NOT NULL DEFAULT 'INITIAL_SERVICE', -- 'INITIAL_SERVICE', 'AMC_ROUTINE', 'WARRANTY_VISIT'
    status VARCHAR(50) NOT NULL DEFAULT 'UNASSIGNED', -- 'UNASSIGNED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
    priority VARCHAR(20) NOT NULL DEFAULT 'NORMAL', -- 'NORMAL', 'URGENT', 'CRITICAL'
    assigned_employee_id UUID REFERENCES employees(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_work_orders_employee ON work_orders(assigned_employee_id);
CREATE INDEX idx_work_orders_status ON work_orders(status);

-- 3. Field Service Visit
CREATE TABLE service_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_number VARCHAR(50) UNIQUE NOT NULL, -- 'SV-2026-00001'
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    primary_employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
    status VARCHAR(30) NOT NULL DEFAULT 'SCHEDULED',
    -- ServiceVisitStatus: SCHEDULED, ON_THE_WAY, ARRIVED, STARTED, COMPLETED, CANCELLED, FAILED
    -- NOTE: This is a SEPARATE state machine from WorkOrderStatus
    scheduled_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_arrival_time TIMESTAMP WITH TIME ZONE,
    actual_start_time TIMESTAMP WITH TIME ZONE,
    actual_completion_time TIMESTAMP WITH TIME ZONE,
    arrival_latitude NUMERIC(10, 8),
    arrival_longitude NUMERIC(11, 8),
    customer_signature_url VARCHAR(500),
    technician_notes TEXT,
    is_customer_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    sync_status VARCHAR(30) NOT NULL DEFAULT 'SYNCED', -- 'SYNCED', 'OFFLINE_PENDING'
    offline_event_id VARCHAR(128),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_service_visits_employee ON service_visits(primary_employee_id);
CREATE INDEX idx_service_visits_status ON service_visits(status);
```

---

### 3.5 Inventory, Chemicals & Material Consumption

```sql
CREATE TABLE chemical_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name VARCHAR(200) NOT NULL,
    chemical_composition VARCHAR(255) NOT NULL,
    registration_number VARCHAR(100), -- Regulatory pesticide license
    unit_of_measure VARCHAR(20) NOT NULL, -- 'LITER', 'ML', 'KG', 'GRAM'
    reorder_level NUMERIC(10, 2) NOT NULL DEFAULT 10.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE chemical_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chemical_product_id UUID NOT NULL REFERENCES chemical_products(id) ON DELETE RESTRICT,
    batch_number VARCHAR(100) NOT NULL,
    manufacturing_date DATE,
    expiry_date DATE NOT NULL,
    total_quantity_received NUMERIC(10, 2) NOT NULL,
    current_quantity_available NUMERIC(10, 2) NOT NULL,
    cost_per_unit NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_batch_qty_nonneg CHECK (current_quantity_available >= 0)
);

CREATE TABLE service_material_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_visit_id UUID NOT NULL REFERENCES service_visits(id) ON DELETE CASCADE,
    chemical_batch_id UUID NOT NULL REFERENCES chemical_batches(id) ON DELETE RESTRICT,
    quantity_used NUMERIC(10, 2) NOT NULL,
    dosage_rate VARCHAR(100),
    target_pest VARCHAR(100),
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3.6 Financial Transactions, Invoices & Expenses

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE RESTRICT,
    payment_method VARCHAR(50) NOT NULL, -- 'ONLINE_GATEWAY', 'CASH_ON_DELIVERY', 'UPI_COLLECT', 'BANK_TRANSFER'
    gateway_name VARCHAR(50), -- 'RAZORPAY', 'STRIPE'
    gateway_order_id VARCHAR(150),
    gateway_payment_id VARCHAR(150),
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'AUTHORIZED', 'PAID', 'PARTIAL', 'FAILED', 'REFUNDED', 'PARTIALLY_REFUNDED'
    idempotency_key VARCHAR(128) UNIQUE,
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_number VARCHAR(50) UNIQUE NOT NULL, -- 'INV-2026-00001'
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE RESTRICT,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    subtotal_amount NUMERIC(12, 2) NOT NULL,
    tax_amount NUMERIC(12, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    pdf_storage_path VARCHAR(500),
    issued_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID REFERENCES agencies(id) ON DELETE SET NULL,
    employee_id UUID REFERENCES employees(id) ON DELETE SET NULL,
    category VARCHAR(100) NOT NULL, -- 'FUEL_CONVEYANCE', 'EQUIPMENT_REPAIR', 'CHEMICAL_RESTOCK', 'OFFICE_RENT'
    amount NUMERIC(12, 2) NOT NULL,
    expense_date DATE NOT NULL,
    description TEXT,
    receipt_file_id UUID,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3.7 Annual Maintenance Contracts (AMC)

```sql
CREATE TABLE amc_contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_number VARCHAR(50) UNIQUE NOT NULL, -- 'AMC-2026-00001'
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    customer_address_id UUID NOT NULL REFERENCES customer_addresses(id) ON DELETE RESTRICT,
    frequency VARCHAR(50) NOT NULL, -- 'MONTHLY', 'BI_MONTHLY', 'QUARTERLY'
    total_visits_contracted INT NOT NULL,
    visits_completed INT NOT NULL DEFAULT 0,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    contract_amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'EXPIRED', 'TERMINATED'
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE amc_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    amc_contract_id UUID NOT NULL REFERENCES amc_contracts(id) ON DELETE CASCADE,
    scheduled_date DATE NOT NULL,
    visit_sequence INT NOT NULL, -- e.g. Visit 1 of 4
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'GENERATED_TO_WORK_ORDER', 'COMPLETED'
    generated_work_order_id UUID REFERENCES work_orders(id) ON DELETE SET NULL,
    CONSTRAINT uq_amc_schedule_contract_seq UNIQUE (amc_contract_id, visit_sequence)
);
```

---

### 3.8 File Storage Metadata & Immutable Audit Trail

```sql
-- Polymorphic File Metadata with Lifecycle Management
-- Allowed entity_type: 'WORK_ORDER', 'SERVICE_VISIT', 'INVOICE', 'EXPENSE', 'CUSTOMER', 'EMPLOYEE'
-- Allowed file_purpose: 'BEFORE_PHOTO', 'AFTER_PHOTO', 'SIGNATURE', 'INVOICE_PDF', 'RECEIPT', 'PROFILE_IMAGE'
CREATE TABLE file_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID REFERENCES agencies(id) ON DELETE RESTRICT,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    file_purpose VARCHAR(100) NOT NULL,
    storage_provider VARCHAR(50) NOT NULL DEFAULT 'AWS_S3',  -- 'AWS_S3', 'GCS', 'MINIO'
    storage_key VARCHAR(1000) NOT NULL UNIQUE,
    file_name VARCHAR(500),
    mime_type VARCHAR(100),
    file_size_bytes BIGINT,
    checksum_sha256 VARCHAR(64),
    file_status VARCHAR(20) NOT NULL DEFAULT 'INITIATED', -- 'INITIATED', 'UPLOADING', 'UPLOADED', 'VERIFIED', 'ATTACHED', 'FAILED', 'ORPHANED'
    uploaded_by UUID REFERENCES users(id),
    access_policy VARCHAR(50) NOT NULL DEFAULT 'PRIVATE',  -- 'PRIVATE', 'AGENCY'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_file_metadata_entity ON file_metadata(entity_type, entity_id);
CREATE INDEX idx_file_metadata_agency ON file_metadata(agency_id);
CREATE INDEX idx_file_metadata_status ON file_metadata(file_status, created_at);

-- Immutable Append-Only Audit Trail
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_id UUID REFERENCES users(id),
    actor_role VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL, -- 'BOOKING_ASSIGNED', 'PRICE_CHANGED', 'INVOICE_ISSUED'
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

-- Database-Level Immutability Enforcement for audit_logs
CREATE OR REPLACE FUNCTION trg_audit_logs_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_logs entries are strictly immutable and cannot be updated or deleted';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_logs_no_update_delete
BEFORE UPDATE OR DELETE ON audit_logs
FOR EACH ROW EXECUTE FUNCTION trg_audit_logs_immutable();

-- Availability Slots (Two-tier booking slot capacity model)
-- employee_id IS NULL: Agency Capacity Pool for service category/territory (capacity >= 1)
-- employee_id IS NOT NULL: Named Technician Calendar Schedule (capacity = 1)
CREATE TABLE availability_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    service_category_id UUID REFERENCES service_categories(id) ON DELETE CASCADE,
    employee_id UUID REFERENCES employees(id) ON DELETE SET NULL,
    service_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 1 CHECK (capacity >= 1),
    booked_count INTEGER NOT NULL DEFAULT 0 CHECK (booked_count >= 0),
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_slot_capacity CHECK (booked_count <= capacity)
);

-- Unique index for Named Technician schedules (prevents overlapping assignments)
CREATE UNIQUE INDEX uq_slot_employee_time
    ON availability_slots(employee_id, service_date, start_time)
    WHERE employee_id IS NOT NULL;

-- Unique index for Agency Capacity Pools
CREATE UNIQUE INDEX uq_slot_agency_pool
    ON availability_slots(agency_id, service_category_id, service_date, start_time)
    WHERE employee_id IS NULL;

CREATE INDEX idx_availability_agency_date ON availability_slots(agency_id, service_date);

-- Coupon Redemptions (per-customer coupon usage tracking)
CREATE TABLE coupon_redemptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coupon_id UUID NOT NULL REFERENCES coupons(id) ON DELETE RESTRICT,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE RESTRICT,
    redeemed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_coupon_redemptions_cust ON coupon_redemptions(coupon_id, customer_id);

-- Payment Events (idempotent webhook event tracking)
CREATE TABLE payment_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID REFERENCES payments(id) ON DELETE RESTRICT,
    provider VARCHAR(50) NOT NULL,
    gateway_event_id VARCHAR(255) NOT NULL,
    gateway_payment_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,
    payload_hash VARCHAR(64) NOT NULL,
    raw_payload JSONB,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    error_message TEXT,
    CONSTRAINT uq_payment_event UNIQUE (provider, gateway_event_id)
);
CREATE INDEX idx_payment_events_payment_id ON payment_events(payment_id);

-- Outbox Events (reliable domain event publication via transactional outbox)
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    payload JSONB NOT NULL,
    payload_version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    publication_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    retry_count INT NOT NULL DEFAULT 0,
    last_error TEXT
);
CREATE INDEX idx_outbox_pending ON outbox_events(publication_status, created_at)
    WHERE publication_status = 'PENDING';

-- Offline Sync Conflicts (technician offline conflict resolution tracking)
CREATE TABLE sync_conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL,
    operation_id UUID NOT NULL,
    agency_id UUID NOT NULL REFERENCES agencies(id),
    entity_type VARCHAR(100) NOT NULL, -- 'SERVICE_VISIT', 'WORK_ORDER'
    entity_id UUID NOT NULL,
    conflict_type VARCHAR(50) NOT NULL, -- 'CLIENT_OVERRIDE_ON_CANCELLED', 'STALE_STATE_COLLISION'
    client_state JSONB NOT NULL,
    server_state JSONB NOT NULL,
    resolution_status VARCHAR(50) NOT NULL DEFAULT 'OPEN', -- 'OPEN', 'AUTO_RESOLVED', 'MANUALLY_RESOLVED'
    resolved_by UUID REFERENCES users(id),
    resolution_notes TEXT,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
CREATE INDEX idx_sync_conflicts_agency ON sync_conflicts(agency_id, resolution_status);

-- Idempotency Keys (API request deduplication with payload fingerprinting)
CREATE TABLE idempotency_keys (
    key VARCHAR(255) PRIMARY KEY,
    tenant_id UUID REFERENCES agencies(id),
    user_id UUID NOT NULL REFERENCES users(id),
    http_method VARCHAR(10) NOT NULL,
    request_path VARCHAR(500) NOT NULL,
    request_hash VARCHAR(64) NOT NULL, -- SHA-256 of request body
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'COMPLETED', 'FAILED'
    response_status INT,
    response_headers JSONB,
    response_body JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours')
);
CREATE INDEX idx_idempotency_lookup ON idempotency_keys(tenant_id, user_id, request_path, key);
CREATE INDEX idx_idempotency_expires ON idempotency_keys(expires_at);
```

---

*This database schema serves as the single source of truth for Flyway migration scripts.*
