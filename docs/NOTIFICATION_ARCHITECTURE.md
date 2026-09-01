# Notification Architecture Specification
## Multi-Channel Communications & Event-Driven Dispatch

**Document Version:** 1.0.0  
**Push Provider:** Firebase Cloud Messaging (FCM HTTP v1 API)  
**SMS / WhatsApp:** MSG91 / Twilio  
**Email Engine:** Spring Mail + Thymeleaf Templates (SendGrid / Resend)  
**Event Broker:** RabbitMQ 3.13.x  
**Date:** September 2026  

---

## 1. Notification Pipeline Overview

The notification subsystem is completely decoupled from synchronous request processing. Domain events published to RabbitMQ trigger background workers that format, personalize, and deliver messages across multiple communication channels:

```text
 ┌───────────────────────────────────┐
 │   Domain Event (e.g. Booking)     │
 └─────────────────┬─────────────────┘
                   │
                   ▼
       [ RabbitMQ: q.notifications ]
                   │
                   ▼
 ┌──────────────────────────────────────────────────┐
 │    Spring Boot Notification Listener Module      │
 │                                                  │
 │  • Resolves User Notification Preferences        │
 │  • Renders Channel-Specific Message Templates    │
 │  • Dispatches to Appropriate Channel Adapters    │
 └─────────────────┬────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┐
        │          │          │          │
        ▼          ▼          ▼          ▼
   ┌─────────┐┌─────────┐┌─────────┐┌─────────┐
   │ FCM Push││ SMS/OTP ││  Email  ││WhatsApp │
   │ Engine  ││ Engine  ││ Engine  ││ (Opt-in)│
   └─────────┘└─────────┘└─────────┘└─────────┘
```

---

## 2. Supported Channels & Event Mapping

| Domain Event | Customer Channel | Technician Channel | Admin Channel |
| :--- | :--- | :--- | :--- |
| `booking.confirmed` | FCM Push + SMS confirmation | — | Web Dashboard Alert |
| `workorder.assigned`| — | High-Priority FCM Push + Sound | Web Dashboard Update |
| `technician.en_route`| FCM Push (*"Tech is on the way"*) | — | Live Dispatch Map |
| `visit.completed` | FCM Push + Email (with PDF Invoice)| FCM Completion Badge | Web Summary |
| `payment.failed` | FCM Push + SMS retry link | — | High-Priority Alert |
| `amc.due_reminder` | FCM Push + WhatsApp reminder | — | Scheduled List |

---

## 3. Firebase Cloud Messaging (FCM) Integration

* **Direct Device Targeting:** User device tokens are stored in `user_device_tokens` table and refreshed on login.
* **FCM Topics:**
  * `broadcast_all_technicians`: Emergency operational alerts.
  * `agency_{agencyId}_dispatch`: Branch-wide notifications.
* **High-Priority Data Payloads:** For technician job assignments, FCM data messages bypass Android Doze mode to ring an audible alert and trigger the local sync worker.

---

## 4. Email & SMS Templating Engine

* **HTML Emails:** Built with **Thymeleaf HTML templates** containing branding, inline CSS, and dynamic placeholders (Customer name, service details, pricing breakdown, tracking URL).
* **PDF Attachments:** Generated invoice PDFs are attached directly to completion emails.
* **Transactional SMS:** Formatted according to regional regulatory templates (e.g., India DLT approved formats).

---

*Governed by event-driven asynchronous processing and reliable messaging standards.*
