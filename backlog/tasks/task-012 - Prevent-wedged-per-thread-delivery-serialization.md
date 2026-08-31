---
id: TASK-012
title: Prevent wedged per-thread delivery serialization
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-29 00:00'
updated_date: '2026-08-31 09:46'
labels:
  - email
  - reliability
  - imap
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
modified_files:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
priority: medium
type: bug
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When `EMAIL_PP_DELETE_PROCESSED` is enabled, inbound mail is serialized per Hermes thread: `_queue_delivery` marks a thread active and the queue only advances when `on_processing_complete` fires and calls `_start_next_delivery`. This assumes the gateway always invokes `on_processing_complete` exactly once per queued event. If that completion is ever missed (dropped message, exception before completion, gateway edge case), the thread remains in `_active_delivery_threads` indefinitely and every subsequent message on that thread is enqueued and never delivered, growing an unbounded silent queue. Add a defensive path so a single missing completion cannot wedge a thread forever.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A thread cannot remain blocked indefinitely because one processing completion was never delivered
- [x] #2 Recovery (timeout, watchdog, or defensive release) advances or abandons a stuck queue without redelivering already-processed mail
- [x] #3 Queue drain, stall, and abandonment are observable via logging
- [x] #4 Tests cover a missing/late `on_processing_complete` and confirm later mail on the same thread is eventually delivered
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Replace the thread-only active guard with active event identity plus a per-delivery watchdog.
2. On watchdog expiry, release only the matching active event and start the next queued event; ignore late completions for an expired event so they cannot release a newer delivery.
3. Preserve existing acknowledgement behavior for late completions, add stall/queue-advance/queue-drained logs, and retain the in-process IMAP UID de-duplication.
4. Add missing- and late-completion regression coverage, then run formatting, lint, type, and test checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Discovered during the 2026-08-29 code review. Relevant code: `_queue_delivery` (adapter.py:849), `_start_next_delivery` (:858), `on_processing_complete` (:871). `_start_next_delivery` is reached only from `on_processing_complete`, which itself returns early unless `delete_processed` is set and `raw_message` is an `_InboundMail`, so any lost completion strands the thread.

Investigation: _fetch_unseen records each UID in _seen before dispatch, so timeout recovery can advance the in-memory queue without redispatching the stalled UID. The active guard must be keyed by event identity because a late completion must not release a newer active event on the same thread.

Implemented a five-minute per-delivery watchdog. Timeout recovery releases only the matching active event and advances the queued event; late completions still acknowledge their own delivery but cannot release a newer active event. Added logs for queueing, watchdog abandonment, advancement, drain, and ignored late completion. Targeted adapter suite passes.

Validation: uv run ruff format --check .; uv run ruff check .; uv run mypy hermes_email_pp; and uv run pytest tests/test_adapter.py -q all passed (30 tests). Full uv run pytest --cov=hermes_email_pp tests/ ran with 56 passed, 1 failed: test_repository_root_has_a_safe_hermes_plugin_scan reports dangerous rather than safe; this is unrelated to TASK-012 and is consistent with existing workspace scan artifacts.

Human updated _DELIVERY_COMPLETION_TIMEOUT to 600 seconds and agreed with the implementation; this supersedes the earlier five-minute timeout reference.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-08-31 09:46
---
Changed the watchdog timeout to 600 seconds and agreed with the implementation.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added event-identity delivery guards with ten-minute watchdog recovery, safe late-completion handling, and queue lifecycle logging. Added a regression that withholds a completion, advances later mail, then sends a late completion while the next event is active. Verified formatting, linting, mypy, and all 30 adapter tests. Full suite has one unrelated plugin-scan failure (56 passed, 1 failed).
<!-- SECTION:FINAL_SUMMARY:END -->
