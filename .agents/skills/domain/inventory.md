---
name: inventory
description: Managing warehouses, technician trunks, and consumable stock.
category: domain
triggers:
  - Receive new stock
  - Transfer stock to technician
  - Record job material usage
inputs:
  - Inventory operations
outputs:
  - Inventory service logic
dependencies:
  - database/inventory-transactions
related_skills:
  - domain/service-visit
---

# Skill: Inventory Domain

## Purpose
To manage the lifecycle of consumable products (chemicals, traps, safety gear) across multiple locations (warehouses, branches, technician vehicles) and track batch expiry.

## When to Use / When NOT to Use
**Use When:** Processing purchase orders, dispatching materials to technicians, and deducting stock after a service visit.
**NOT to Use:** For non-stock tracking or general accounting.

## Required Context
Inventory requires strict transactional boundaries. Stock is deducted based on `service_material_usage` records created during a `Service Visit`.

## Domain Rules & Constraints
1. **Locations:** Inventory exists at a `Location`. A location can be a 'Warehouse', 'Branch', or 'Technician Trunk'.
2. **Batches:** Chemicals expire. All stock movements must reference a `batch_id` to enforce FIFO (First-In, First-Out) consumption.
3. **Double Entry:** A transfer from a Branch to a Trunk creates two ledger entries: `-X` at Branch, `+X` at Trunk.

## Entity Structure
*   `inventory_products`: `id`, `name`, `sku`, `unit_of_measure`, `minimum_stock_level`
*   `inventory_batches`: `id`, `product_id`, `batch_number`, `expiry_date`
*   `inventory_locations`: `id`, `name`, `type` (WAREHOUSE, TRUNK), `owner_id` (nullable, links to employee)
*   `inventory_transactions`: The ledger (see `database/inventory-transactions`)

## Spring Service Methods
*   `void receiveStock(ReceiveStockDto dto)`
*   `void transferStock(UUID fromLocation, UUID toLocation, UUID productId, BigDecimal quantity)`
*   `void consumeStock(UUID locationId, UUID productId, BigDecimal quantity, UUID serviceVisitId)`

## API Endpoints
*   `GET /api/v1/inventory/products`
*   `POST /api/v1/inventory/transfer`
*   `GET /api/v1/inventory/locations/{id}/balance`

## Database Considerations
*   Use aggregate views or cached tables for current stock balances to avoid summing the entire ledger on every read.
*   Use row-level locking (`SELECT ... FOR UPDATE`) during stock deductions to prevent race conditions.

## RabbitMQ Events
*   `LowStockAlertEvent` -> Triggered when balance drops below `minimum_stock_level`.

## Validation Checklist
- [ ] Is FIFO batch deduction implemented correctly?
- [ ] Are race conditions mitigated using database locks or Redis distributed locks?
- [ ] Are location transfers atomic?

## Common Mistakes
*   Deducting generic product stock without specifying the batch.
*   Not locking the balance calculation during concurrent deductions, leading to negative stock.

## Related Skills
- `database/inventory-transactions`
- `domain/service-visit`
