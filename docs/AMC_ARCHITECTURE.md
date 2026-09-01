# Annual Maintenance Contract (AMC) Architecture Specification
## Recurring Services, Scheduled Visit Generation & Contract Lifecycle

**Document Version:** 1.0.0  
**Scheduler Engine:** Spring `@Scheduled` / Quartz Scheduler  
**Database:** PostgreSQL 16  
**Date:** September 2026  

---

## 1. AMC Business & Domain Model

Annual Maintenance Contracts (AMCs) provide predictable recurring revenue and customer retention for pest control businesses. A single AMC contract spans 12 months with pre-defined service frequencies.

```text
 ┌──────────────────────────────────────────────────────────┐
 │                       AMC Contract                       │
 │  • Customer, Target Address, Service Type, Total Visits  │
 │  • Contract Value, Payment Terms, Validity Period        │
 └────────────────────────────┬─────────────────────────────┘
                              │ 1:N
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │                      AMC Schedules                       │
 │  • Visit 1: 15-Sep-2026 (Status: COMPLETED)              │
 │  • Visit 2: 15-Dec-2026 (Status: GENERATED_TO_WO)        │
 │  • Visit 3: 15-Mar-2027 (Status: PENDING)                │
 │  • Visit 4: 15-Jun-2027 (Status: PENDING)                │
 └────────────────────────────┬─────────────────────────────┘
                              │ Automated Cron (7 Days Prior)
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │                    Generated Work Order                  │
 │  • Enters Dispatch Board: Ready for Technician Assignment│
 └──────────────────────────────────────────────────────────┘
```

---

## 2. Automated Scheduled Visit Generator

A Spring Boot scheduled background process runs daily at `01:00 UTC`:

```java
@Component
public class AmcVisitGeneratorTask {

    @Scheduled(cron = "0 0 1 * * ?") // Daily at 01:00 AM
    @Transactional
    public void generateUpcomingAmcWorkOrders() {
        LocalDate targetDate = LocalDate.now().plusDays(7);
        List<AmcSchedule> dueSchedules = amcScheduleRepository
            .findPendingSchedulesDueBy(targetDate);

        for (AmcSchedule schedule : dueSchedules) {
            WorkOrder wo = workOrderService.createFromAmcSchedule(schedule);
            schedule.setStatus(AmcScheduleStatus.GENERATED_TO_WORK_ORDER);
            schedule.setGeneratedWorkOrderId(wo.getId());
            
            notificationService.sendAmcVisitUpcomingAlert(schedule);
        }
    }
}
```

## Cron Idempotency

The daily AMC scheduling job is idempotent:
```sql
-- Prevents duplicate work order generation for same AMC schedule
CREATE UNIQUE INDEX uq_amc_schedule_date 
    ON amc_schedules(contract_id, scheduled_date);
```

The Spring @Scheduled job uses INSERT ... ON CONFLICT DO NOTHING. Running the job multiple times for the same day is safe.

## Conflict with Offline Sync
If a technician completes an AMC visit offline and later a second visit is auto-generated for the same slot by the scheduler:
1. Server detects conflict on sync
2. Auto-generated visit is marked DUPLICATE and suppressed
3. DISPATCHER notified
4. Audit logged

---

## 3. Contract Renewal & Expiry Engine

* **30-Day Renewal Window:** 30 days prior to `end_date`, the system emits `amc.renewal_due`, triggering an in-app renewal banner on the Customer App and a WhatsApp renewal quote.
* **Auto-Renewal Workflows:** If approved, a new contract is generated, linking the service history for unbroken warranty coverage.

## Timezone Handling
All scheduled dates stored in UTC. UI displays in local timezone (Asia/Kolkata for India deployments). Spring @Scheduled cron runs at 01:00 UTC daily. Customer-facing visit dates formatted by the frontend based on user locale.

---

*Governed by enterprise contract management and recurring subscription scheduling patterns.*
