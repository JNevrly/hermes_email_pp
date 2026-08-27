---
id: TASK-010
title: Delete successfully processed Email++ mail
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-27 16:08'
updated_date: '2026-08-27 17:50'
labels:
  - email
  - imap
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
  - README.md
priority: high
type: feature
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provide opt-in cleanup for the dedicated agent mailbox. Authorized email is deleted only once Hermes has completed successfully and its response has been accepted by SMTP. Rejected, failed, cancelled, and malformed mail remains available for inspection and recovery.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 An opt-in setting exposes processed-email deletion without changing the default mailbox behavior
- [x] #2 Authorized messages are deleted only after a successful Hermes processing outcome and SMTP-accepted response
- [x] #3 Rejected, malformed, cancelled, failed, and response-delivery-failed mail is retained
- [x] #4 Deletion uses verified UID and UIDVALIDITY state, requires UIDPLUS, and never performs a broad EXPUNGE
- [x] #5 Successful processing is not rerun when deletion is retried after an IMAP failure or restart
- [x] #6 Documentation and automated tests cover configuration, outcomes, safe deletion, and recovery
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a validated opt-in deletion setting and document its default-safe behavior.
2. Carry UID and UIDVALIDITY through inbound dispatch, use non-mutating IMAP fetches, and retain explicit acknowledgement state.
3. Correlate terminal Hermes processing outcomes with SMTP delivery, then perform UIDPLUS-only targeted deletion with retryable pending acknowledgements.
4. Preserve rejected and unsuccessful mail; add regression tests for all outcomes, safe IMAP commands, and restart recovery.
5. Run formatting, lint, type, and test checks; record results for review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented opt-in EMAIL_PP_DELETE_PROCESSED across configuration, dashboard metadata, plugin manifest, and README. The adapter fetches cleanup-enabled mail with BODY.PEEK[], serializes delivery per Hermes thread, persists UIDVALIDITY-bound pending acknowledgements, and deletes only after SUCCESS plus SMTP delivery. Deletion uses UID STORE plus UID EXPUNGE only when UIDPLUS is available; rejected mail is marked seen and retained, while failed or cancelled mail is released for retry.

Validation passed: focused adapter and configuration tests run with coverage reached 54 passing tests at 100%. Ruff formatting and lint checks and MyPy passed. Full pytest has 54 passing tests and one known unrelated plugin_guard failure caused by the pre-existing .release-venv workspace contamination.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-08-27 16:22
---
Agent: Implementation is ready for human review. All six acceptance criteria are verified by focused automated tests; the only full-suite failure is the pre-existing plugin_guard scan of .release-venv.
---

author: @human
created: 2026-08-27 17:50
---
Human: Reviewed the processed-email cleanup implementation and approved closing the task.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added opt-in processed-email cleanup with UIDVALIDITY-bound persistent acknowledgement records, non-mutating IMAP fetches, per-thread delivery serialization, and UIDPLUS-only targeted deletion after Hermes SUCCESS plus SMTP-accepted response. Rejected and malformed mail is retained and marked seen; failed or cancelled processing remains available for retry. Documentation and configuration surfaces were updated. Focused test suite passes at 100% coverage; full pytest is blocked only by the known pre-existing plugin_guard .release-venv failure.
<!-- SECTION:FINAL_SUMMARY:END -->
