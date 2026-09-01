---
name: notifications
description: Managing multi-channel asynchronous communications.
category: domain
triggers:
  - Send SMS/Email/Push
  - Process NotificationRequested events
inputs:
  - Notification payload
outputs:
  - Message delivery
dependencies:
  - messaging/rabbitmq-consumer
related_skills:
  - backend/fcm-integration
---

# Skill: Notification Domain

## Purpose
To handle all outbound communication from the ERP to customers, technicians, and admins across various channels (SMS, Email, Push Notifications, WhatsApp).

## When to Use / When NOT to Use
**Use When:** Sending OTPs, booking confirmations, technician arrival alerts, or daily summaries.
**NOT to Use:** For synchronous API responses. Notifications are almost always asynchronous.

## Required Context
Notifications are side-effects. They should be decoupled from core business transactions using RabbitMQ to prevent external API failures (e.g., Twilio being down) from rolling back a successful database transaction.

## Domain Rules & Constraints
1. **Asynchronous Execution:** The core service publishes a `NotificationRequestedEvent` to RabbitMQ. The Notification Service consumes it.
2. **Multi-Channel:** Support routing to Firebase Cloud Messaging (FCM) for mobile apps, Thymeleaf for HTML Emails, and third-party APIs (MSG91/Twilio) for SMS/WhatsApp.
3. **Retry & DLQ:** If a provider is down, the message should be retried with exponential backoff. If it fails repeatedly, route to a Dead Letter Queue (DLQ).
4. **Audit Trail:** Log all sent notifications in a `notifications` database table for customer support debugging.

## Entity Structure
*   `notifications`: `id`, `recipient_id`, `recipient_type` (CUSTOMER, EMPLOYEE), `channel` (SMS, EMAIL, PUSH), `message_body`, `status` (PENDING, SENT, FAILED), `external_reference_id`, `created_at`

## Spring Service Methods
*   `void requestNotification(NotificationRequest request)` (Publishes to RabbitMQ)
*   `@RabbitListener void handleNotificationEvent(NotificationEvent event)`
*   `void sendPush(String fcmToken, String title, String body)`

## API Endpoints
*   Usually internal only. Frontend rarely triggers notifications directly; they are triggered by domain events.

## Database Considerations
*   The `notifications` table grows rapidly. Consider partitioning it by month or purging records older than 90 days.

## RabbitMQ Events
*   Consumes: Almost any domain event (`BookingConfirmedEvent`, `WorkOrderAssignedEvent`, etc.)
*   Internal: `NotificationRequestedEvent`

## Validation Checklist
- [ ] Is communication strictly asynchronous via RabbitMQ?
- [ ] Are failures routed to a Dead Letter Queue?
- [ ] Is a record of the message kept in the database for auditing?
- [ ] Are HTML emails rendered using a template engine like Thymeleaf?

## Common Mistakes
*   Sending an email synchronously in the same thread as the web request, causing the user to wait 3 seconds for the page to load.
*   Failing a critical business transaction because an SMS provider API returned a 500 error.

## Related Skills
- `messaging/rabbitmq-consumer`
- `messaging/dead-letter-queues`
