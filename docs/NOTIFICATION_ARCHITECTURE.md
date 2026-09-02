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

| Domain Event (PascalCase) | Customer Channel | Technician Channel | Admin Channel |
| :--- | :--- | :--- | :--- |
| `BookingConfirmed` | FCM Push + SMS confirmation | — | Web Dashboard Alert |
| `TechnicianAssigned` | — | High-Priority FCM Push + Sound | Web Dashboard Update |
| `TechnicianEnRoute` | FCM Push (*"Tech is on the way"*) | — | Live Dispatch Map |
| `ServiceVisitCompleted` | FCM Push + Email (with PDF Invoice)| FCM Completion Badge | Web Summary |
| `PaymentFailed` | FCM Push + SMS retry link | — | High-Priority Alert |
| `AMCVisitDueReminder` | FCM Push + WhatsApp reminder | — | Scheduled List |

---

## 3. Firebase Cloud Messaging (FCM) Integration

* **Direct Device Targeting:** User device tokens are stored in `device_tokens` table and refreshed on login.
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

## 5. Notification Persistence & Outbox Integration

Important notifications (booking confirmation, payment receipt, technician assignment) are persisted to the `notifications` table in PostgreSQL before or during dispatch. This provides:
- Delivery retry capability (if FCM/SMS fails, notification record exists for re-delivery).
- Notification history for the customer app ("Your Notifications" feed).
- Audit trail for regulatory and dispute purposes.

---

## 6. Notification Provider Abstraction Architecture

To isolate the domain from third-party vendor APIs, the notification module uses a provider port-and-adapter architecture:

```text
[ Notification Service ]
           │
           ▼
[ NotificationChannelPort ]
           │
           ├──► FcmPushProviderAdapter       (Firebase Admin SDK HTTP v1)
           ├──► SmsProviderAdapter           (Twilio / MSG91 DLT compliant)
           ├──► EmailProviderAdapter         (SendGrid / Resend via SMTP/REST)
           └──► WhatsAppProviderAdapter      (Meta WhatsApp Cloud API)
```

* **Provider Selection Strategy:**
  - **Configuration-Driven:** Active provider per channel is configured in `application.yml` (e.g. `notification.sms.active-provider=msg91`).
  - **Fallback-Driven:** If primary push notification (FCM) fails to deliver within 5 minutes for a critical operational event (`BookingConfirmed`), the system automatically falls back to transactional SMS dispatch.

