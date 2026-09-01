---
id: TASK-015
title: Reuse IMAP and SMTP connections across operations
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-29 00:00'
updated_date: '2026-09-01 10:07'
labels:
  - email
  - imap
  - performance
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
priority: low
type: chore
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every poll cycle opens a new `IMAP4_SSL`, logs in, and logs out, and each side operation — deletion retries, marking mail seen, and every outbound send — opens its own connection and re-authenticates. At the default 15-second poll interval, plus per-message side effects when deletion is enabled, this produces frequent TLS handshakes and LOGIN round-trips, and some providers throttle rapid re-logins. Maintain a persistent authenticated session for the poll hot path (reconnecting on error) and consider reusing an SMTP connection for bursts of sends.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The IMAP poll path reuses an authenticated session across cycles instead of reconnecting each poll
- [x] #2 Connection errors trigger a clean reconnect without losing UIDVALIDITY/seen state or reprocessing mail
- [x] #3 Deletion, mark-seen, and send paths reuse a session where safe, or the trade-off is documented
- [x] #4 Tests cover reconnect-on-error and confirm no duplicate processing across a reconnect
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add one lock-protected, authenticated IMAP client per adapter and close it after all outstanding IMAP workers finish.
2. Run polling, deletion retry, and mark-seen commands through the shared client; on a transport or IMAP error retire it, reconnect, reselect the mailbox, and retry the idempotent operation once.
3. Preserve in-memory UIDVALIDITY/seen state during same-generation reconnects, use endpoint-specific mailbox cache keys, and reset safely after a UIDVALIDITY change.
4. Keep SMTP connections per send because retrying an uncertain SMTP DATA result can duplicate mail; document that trade-off.
5. Add mocked reconnect tests for reuse, no duplicate fetches, state preservation, and serialized cleanup; run lint, type, and tests.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Discovered during the 2026-08-29 code review. Per-operation connections are created in `_fetch_unseen`, `_retry_pending_deletions`, `_mark_seen`, and `_send_email`/`_smtp`. This is intentionally simple today; the change is an efficiency/robustness improvement, not a correctness fix, so preserve the existing UID-safe semantics.

Investigation (2026-09-01): TASK-015 was not implemented. `_fetch_unseen` created/logged in/logged out an IMAP client per poll; poll errors were treated as fatal. `_retry_pending_deletions` and `_mark_seen` also created separate clients. A shared session must serialize IMAP use across poll, dispatch completion, and shutdown; preserve UIDVALIDITY checks and targeted UIDPLUS expunge. The existing reconnect test did not inject a transport error or prove no duplicate dispatch. Mailbox state was keyed only by address and mailbox, unlike pending deletion storage, so it could be shared incorrectly between endpoints.

Implementation (2026-09-01): Added an adapter-owned `threading.Lock`-protected IMAP client. Polling, deletion retries, and mark-seen now share it. `_with_imap` retires a failed client, reconnects once, and reselects via each operation's existing mailbox validation. Fetching stages seen UIDs locally until the complete poll succeeds, avoiding loss after a partial-poll reconnect. Disconnect waits for in-flight IMAP work before logout. Mailbox state cache keys now include IMAP host and port. SMTP intentionally remains per-send because a failed or unknown SMTP DATA response cannot be retried safely without possible duplicate delivery.

Validation (2026-09-01): uv run pytest -q passed (60 tests); uv run ruff format --check hermes_email_pp tests and uv run ruff check hermes_email_pp tests passed; uv run mypy hermes_email_pp passed; git diff --check passed.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-09-01 10:01
---
Human: Approved implementation of TASK-015 after the issue review.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented a serialized persistent IMAP client for polling, deletion retry, and mark-seen operations. It retires and reconnects once after IMAP/transport errors, preserves same-generation state, stages poll seen state transactionally, and closes safely on disconnect. SMTP remains per-send to avoid duplicate delivery after an ambiguous DATA failure. Added connection reuse and reconnect/no-duplicate tests. Verified with 60 passing tests, Ruff formatting/lint, mypy, and git diff --check.
<!-- SECTION:FINAL_SUMMARY:END -->
