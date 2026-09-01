---
name: technician-attachment-upload
description: Skill for uploading photos/signatures to Object Storage.
category: android
triggers:
  - upload attachments
inputs:
  - local files
outputs:
  - object storage keys
dependencies: []
related_skills:
  - technician-service-execution
---

# technician-attachment-upload

## Purpose
Skill for uploading photos/signatures to Object Storage. Cover: pre-signed URL pattern (GET /api/v1/files/upload-url), direct upload to storage, retry queue for failed uploads, file_metadata record in PostgreSQL.

## When to Use
Uploading heavy media files from the technician app.

## When NOT to Use
For small JSON sync payloads.

## Required Context
- Object storage integration

## Inputs
- Compressed image files

## Expected Outputs
- Accessible URLs

## Rules & Constraints
1. Must use pre-signed URLs.
2. Do not pass binary data through the Spring Boot API directly if large.
3. Queue uploads for offline support.

## Step-by-Step Workflow
1. Request pre-signed URL from backend.
2. Upload file directly to Object Storage (S3/GCS) via HTTP PUT.
3. Notify backend of successful upload to save metadata.

## Validation Checklist
- [ ] Pre-signed URLs expire quickly.
- [ ] Backend tracks file metadata.

## Common Mistakes
- Uploading large images directly to the API, eating memory.

## Example Usage
```kotlin
// Pre-signed URL fetch
```

## Related Skills
- technician-service-execution

<!-- Padding -->
<!-- 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 -->
