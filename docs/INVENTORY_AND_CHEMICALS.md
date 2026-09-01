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

---

## 4. Cost of Goods Sold (COGS) Integration

* Every chemical batch carries a `cost_per_unit`.
* When a service visit is completed, the exact material cost is computed:
  $$\text{Material COGS} = \sum (\text{Quantity Used} \times \text{Batch Unit Cost})$$
* This metric feeds directly into the profitability dashboard to calculate accurate gross margins per job and per technician.

---

*Governed by environmental safety compliance and enterprise ERP inventory standards.*
