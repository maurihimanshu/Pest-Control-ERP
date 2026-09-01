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

---

## 3. Contract Renewal & Expiry Engine

* **30-Day Renewal Window:** 30 days prior to `end_date`, the system emits `amc.renewal_due`, triggering an in-app renewal banner on the Customer App and a WhatsApp renewal quote.
* **Auto-Renewal Workflows:** If approved, a new contract is generated, linking the service history for unbroken warranty coverage.

---

*Governed by enterprise contract management and recurring subscription scheduling patterns.*
