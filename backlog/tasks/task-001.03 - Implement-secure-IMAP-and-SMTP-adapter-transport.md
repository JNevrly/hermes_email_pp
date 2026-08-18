---
id: TASK-001.03
title: Implement secure IMAP and SMTP adapter transport
status: To Do
assignee: []
created_date: '2026-08-18 12:54'
labels: []
dependencies:
  - TASK-001.02
references:
  - >-
    https://github.com/NousResearch/hermes-agent/blob/e02d1e41fc6104187e20af9eac8b2820566e3508/plugins/platforms/email/adapter.py
parent_task_id: TASK-001
priority: high
type: task
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the BasePlatformAdapter lifecycle for receiving mail over IMAP and sending through SMTP while retaining the security and reliability properties required for a terminal-capable Hermes channel. Inbound messages must be normalized into MessageEvent instances using the per-thread routing context, and all outbound attachment types must use a single fail-closed recipient resolution path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The adapter validates configuration, connects, polls, reconnects, and disconnects without blocking the asyncio event loop
- [ ] #2 IMAP uses TLS and SMTP supports implicit TLS on port 465 plus verified STARTTLS on other configured ports
- [ ] #3 Existing inbox messages are baselined on first startup and duplicate processing is bounded across polling and same-process reconnects
- [ ] #4 Access is default-deny and supports EMAIL_PP_ALLOWED_USERS plus the explicit allow-all override
- [ ] #5 Self messages, automated senders, and unauthenticated spoofed allowlist identities are rejected before Hermes processing
- [ ] #6 Plain, HTML-only, multipart, image, and document inbound messages are decoded safely and represented correctly to Hermes
- [ ] #7 Text, image, document, and audio outbound paths resolve only an explicit recipient and never fall back to an unrelated cached sender
- [ ] #8 Transport and per-message failures are surfaced without leaking connections or preventing unrelated messages from being processed
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Ruff check and format check pass
- [ ] #2 MyPy passes for the package
- [ ] #3 Pytest passes with the configured coverage threshold
<!-- DOD:END -->
