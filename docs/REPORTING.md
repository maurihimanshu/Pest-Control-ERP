# Reporting & Analytics Specification
## Operational KPIs, Financial Statements & Reporting Pipeline

**Document Version:** 1.0.0  
**Data Engine:** PostgreSQL 16 (Relational Queries & Materialized Views)  
**Export Engine:** Apache POI (Excel), OpenCSV, OpenPDF  
**Date:** September 2026  

---

## 1. Reporting Architecture Overview

The reporting architecture uses a two-tier approach:
1. **Live Operational Dashboard:** Real-time queries for today's active dispatch, technician workload, and pending bookings.
2. **Aggregated Analytical Reports:** Pre-computed daily summary tables (`daily_financial_summary`, `technician_performance_daily`) populated via a nightly Spring Boot aggregation task to ensure instant load times without straining transactional tables.

```text
 ┌──────────────────────────────────────────────────────────┐
 │                  PostgreSQL Relational DB                │
 │    bookings • service_visits • payments • expenses       │
 └────────────────────────────┬─────────────────────────────┘
                              │ Nightly Aggregator Job
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │             Pre-Aggregated Materialized Tables           │
 │  • daily_financial_summary   • technician_performance    │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │                Admin Web Analytics Dashboard             │
 │  • Live KPI Cards • Recharts Visuals • CSV / PDF Exports │
 └──────────────────────────────────────────────────────────┘
```

---

## 2. Core Operational & Financial Reports

| Report Name | Scope | Metrics Included | Target Persona |
| :--- | :--- | :--- | :--- |
| **Executive Daily KPI** | Company-Wide | Today's bookings, revenue, jobs in progress, cancellations | Super Admin |
| **Technician Performance**| Employee-Level | Total assigned, completion rate %, avg job duration, rating | Operations / Admin |
| **Branch Profit & Loss** | Agency / Branch| Gross revenue, chemical COGS, payouts, expenses, net margin | Branch Mgr / Admin |
| **Chemical Consumption** | Inventory | Quantity used per chemical, waste %, cost per service visit | Quality Auditor |
| **AMC Contract Pipeline** | Commercial | Active contracts, upcoming renewal %, churn rate | Commercial Sales |

---

## 3. Asynchronous Export Generation

For heavy date-range exports ($> 5,000$ rows):
* Admin clicks *"Export CSV / Excel"*.
* Spring Boot enqueues an export job via RabbitMQ (`q.reports.export`).
* Worker renders the spreadsheet, uploads to Object Storage, and notifies the Admin via in-app toast with a direct download link.

---

*Governed by enterprise business intelligence and financial reporting standards.*
