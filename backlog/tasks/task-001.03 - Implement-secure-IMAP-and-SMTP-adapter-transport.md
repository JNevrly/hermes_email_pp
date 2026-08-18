---
id: TASK-001.03
title: Implement secure IMAP and SMTP adapter transport
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-18 12:54'
updated_date: '2026-08-18 14:01'
labels: []
dependencies:
  - TASK-001.02
references:
  - >-
    https://github.com/NousResearch/hermes-agent/blob/e02d1e41fc6104187e20af9eac8b2820566e3508/plugins/platforms/email/adapter.py
modified_files:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
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
- [x] #1 The adapter validates configuration, connects, polls, reconnects, and disconnects without blocking the asyncio event loop
- [x] #2 IMAP uses TLS and SMTP supports implicit TLS on port 465 plus verified STARTTLS on other configured ports
- [x] #3 Existing inbox messages are baselined on first startup and duplicate processing is bounded across polling and same-process reconnects
- [x] #4 Access is default-deny and supports EMAIL_PP_ALLOWED_USERS plus the explicit allow-all override
- [x] #5 Self messages, automated senders, and unauthenticated spoofed allowlist identities are rejected before Hermes processing
- [x] #6 Plain, HTML-only, multipart, image, and document inbound messages are decoded safely and represented correctly to Hermes
- [x] #7 Text, image, document, and audio outbound paths resolve only an explicit recipient and never fall back to an unrelated cached sender
- [x] #8 Transport and per-message failures are surfaced without leaking connections or preventing unrelated messages from being processed
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Ruff check and format check pass
- [x] #2 MyPy passes for the package
- [x] #3 Pytest passes with the configured coverage threshold
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement an EmailPPAdapter using only EMAIL_PP_* settings and the BasePlatformAdapter contract, with TLS IMAP/SMTP helpers, bounded reconnect-safe UID tracking, and non-blocking worker-thread I/O.
2. Normalize and authorize inbound RFC messages before dispatch, including safe MIME decoding, attachment caching, sender authentication checks, and ThreadRoute-backed SessionSource construction.
3. Implement text, image, document, and audio egress through one recipient-and-thread resolver, then add mocked transport tests for lifecycle, security, MIME, routing, and error containment.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation checkpoint: added hermes_email_pp/adapter.py with fallback test-only Hermes types, isolated EMAIL_PP_* configuration, TLS IMAP/SMTP lifecycle, bounded reconnect-safe UID snapshots, default-deny authenticated sender checks, MIME/attachment normalization, EmailThreadRouter SessionSource routing, and explicit reply-route-only egress for text/image/document/audio. Ruff and MyPy pass. Remaining: add mocked IMAP/SMTP/Hermes tests for the adapter; current pytest coverage gate fails because the new adapter has no direct tests yet.

Added tests/test_adapter.py with mocked IMAP, SMTP, routing, and Hermes-boundary tests. It verifies TLS mode selection, first-start/reconnect UID baselining, bounded deduplication, default-deny and authenticated sender gates, MIME and attachment representation, explicit-route text/image/document/audio egress, lifecycle error handling, and malformed per-message containment. Validation passed: .venv/bin/ruff check . && .venv/bin/ruff format --check .; .venv/bin/mypy hermes_email_pp; .venv/bin/pytest --cov=hermes_email_pp tests/ (20 passed, 100% coverage).
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-08-18 14:01
---
Agent: Ready for human review. Mocked transport coverage verifies all acceptance criteria; live mailbox integration remains reserved for the final validation task.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the Email++ BasePlatformAdapter transport with isolated EMAIL_PP_* settings, non-blocking TLS IMAP/SMTP lifecycle, reconnect-safe bounded UID tracking, authenticated default-deny inbound authorization, MIME/attachment normalization, and EmailThreadRouter-backed sources. All egress paths require an explicit recipient plus known reply route, so text, image, document, and audio sends cannot borrow another sender context. Mocked IMAP/SMTP tests validate lifecycle, TLS modes, MIME, security gates, routing, errors, and malformed responses. Ruff and MyPy pass; Pytest reports 20 passing tests and 100% package coverage. No ADRs or follow-up tasks created.
<!-- SECTION:FINAL_SUMMARY:END -->
