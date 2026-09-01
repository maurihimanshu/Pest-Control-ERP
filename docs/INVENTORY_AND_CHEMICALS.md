# Inventory & Chemical Management Specification
## Stock Tracking, Batch Expiry, Trunk Stock & Material Usage

**Document Version:** 1.0.0  
**Backend Framework:** Spring Boot 3.3.x  
**Database:** PostgreSQL 16  
**Date:** September 2026  

---

## 1. Inventory & Chemical Domain Overview

In pest control operations, chemical inventory represents a significant operational cost and a regulatory compliance requirement. The ERP tracks chemicals from supplier procurement down to individual service visit consumption.

```text
 ┌─────────────────────────┐
 │   Chemical Product      │ (e.g. Imidacloprid 30.5% SC)
 └────────────┬────────────┘
              │ 1:N
 ┌────────────▼────────────┐
 │    Chemical Batch       │ (Batch #, Expiry Date, Unit Cost)
 └────────────┬────────────┘
              │
              ▼ (Transfer & Allocation)
 ┌──────────────────────────────────────────────────────────┐
 │                  Inventory Locations                     │
 │  Central Warehouse  ──►  Branch Warehouse  ──► Technician│
 │                                                  Trunk   │
 └────────────────────────────┬─────────────────────────────┘
                              │ Field Consumption
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │                 Service Material Usage                   │
 │  Service Visit SV-2026-00042: 50 ml applied for Cockroach│
 └──────────────────────────────────────────────────────────┘
```

---

## 2. Multi-Tier Inventory Hierarchy

1. **Central Warehouse:** Master storage where bulk chemical procurement shipments are received and quality-checked.
2. **Branch / Agency Warehouse:** Regional distribution points where local inventory is stocked.
3. **Technician Trunk Stock:** The physical inventory allocated to a technician's service vehicle or kit.
4. **Service Visit Consumption:** The exact dosage deducted from technician trunk stock upon completing a treatment.

---

## 3. Batch Expiry & Regulatory Tracking (FIFO)

* **First-In, First-Out (FIFO):** When allocating stock to technicians, the system automatically suggests batches closest to expiration to minimize waste.
* **Expiry Alerts:** A daily Spring Boot scheduled job scans `chemical_batches` and alerts branch managers 60, 30, and 15 days before batch expiration.
* **Dosage Auditing:** Every `service_material_usage` entry records chemical batch ID, quantity used, target pest, and dosage rate, providing full traceability for environmental audits.

## Inventory Deduction — Transactional Safety

Inventory deductions are performed within the SAME PostgreSQL transaction as service visit completion:

```sql
-- PostgreSQL-enforced safety constraint
ALTER TABLE chemical_batches 
    ADD CONSTRAINT chk_batch_qty_nonneg CHECK (current_quantity >= 0);
```

Deduction Flow:
```
BEGIN TRANSACTION
  FOR EACH material in request.materialsUsed:
    SELECT * FROM chemical_batches WHERE id = ? FOR UPDATE  -- prevents concurrent deduction
    VALIDATE: current_quantity >= used_quantity
    VALIDATE: NOT batch.is_expired
    UPDATE chemical_batches SET current_quantity = current_quantity - used_quantity
    INSERT inventory_transactions (type='SERVICE_DEDUCTION', qty_change = -used_qty, ref_visit_id)
    INSERT service_material_usage (visit_id, batch_id, used_qty, dosage_rate)
  UPDATE service_visits SET status = 'COMPLETED'
  INSERT outbox_events (type='ServiceCompleted')
COMMIT
```

On Visit Cancellation After Deduction:
- NOT a database rollback (would lose audit trail)
- Creates a REVERSAL inventory_transaction: type='CANCELLATION_REVERSAL', qty_change = +used_qty
- Audit log records both the original deduction and the reversal

Duplicate Sync Requests:
- Handled by operation_id idempotency — server checks if operation_id was already processed
- Duplicate sync does NOT cause double-deduction

---

## 4. Cost of Goods Sold (COGS) Integration

* Every chemical batch carries a `cost_per_unit`.
* When a service visit is completed, the exact material cost is computed:
  $$\text{Material COGS} = \sum (\text{Quantity Used} \times \text{Batch Unit Cost})$$
* This metric feeds directly into the profitability dashboard to calculate accurate gross margins per job and per technician.

---

*Governed by environmental safety compliance and enterprise ERP inventory standards.*
