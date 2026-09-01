---
name: fcm-integration
description: Sends FCM push notifications from Spring Boot using HTTP v1 API.
category: backend
triggers:
  - send push notification
  - fcm
inputs:
  - notification payload
  - target token/topic
outputs:
  - Push notification dispatch logic
dependencies:
  - architecture-rules
related_skills:
  - service-layer
---

# Skill: FCM Integration

## Purpose
To alert users (Customers or Technicians) of important state changes asynchronously via Firebase Cloud Messaging.

## Rules & Constraints
1. Use the **FCM HTTP v1 API** (via Firebase Admin SDK). Legacy FCM API is deprecated.
2. Send notifications asynchronously (e.g., via Spring `@Async` or consuming a RabbitMQ event). Never block an HTTP API request to send a push notification.
3. Manage device tokens in PostgreSQL (Users have one-to-many DeviceTokens).
4. Handle stale tokens gracefully (remove them from PostgreSQL if FCM returns a `UNREGISTERED` error).

## Step-by-Step Workflow
1. Ensure Firebase Admin SDK is initialized.
2. Construct the `Message` object using `Message.builder()`.
3. Set the `Notification` (title, body) and any custom `Data` payload.
4. Send via `FirebaseMessaging.getInstance().sendAsync(message)`.
5. Add a callback/listener to handle the result. If the error is `MessagingErrorCode.UNREGISTERED`, delete the device token from the database.

## Validation Checklist
- [ ] Non-blocking execution (Async/Events).
- [ ] Token cleanup logic implemented.
- [ ] Payload size respects FCM limits (4KB data payload).

## Common Mistakes
- Calling FCM synchronously inside a `@Transactional` block, tying up database connections during network delays.
- Hardcoding string topics instead of managing a structured ENUM or configuration.
