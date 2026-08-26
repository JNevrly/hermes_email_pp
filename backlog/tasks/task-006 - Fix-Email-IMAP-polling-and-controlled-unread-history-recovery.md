---
id: TASK-006
title: Fix Email++ IMAP polling and controlled unread-history recovery
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-26 16:13'
updated_date: '2026-08-26 18:44'
labels:
  - email
  - imap
  - observability
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - hermes_email_pp/config.py
  - tests/test_adapter.py
  - README.md
  - plugin.yaml
priority: high
type: bug
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Correct Email++ IMAP polling for servers that require an omitted IMAP charset to be sent as None, not an empty string. Add operator-controlled recovery of unread messages that existed before a cold gateway start, and make the IMAP polling lifecycle diagnosable without logging credentials, message bodies, or authentication headers.

Confirmed production evidence: against mail.alps.cz:993, UID SEARCH with None charset returns four unseen messages while the current UID SEARCH with an empty-string charset returns zero. The current adapter uses the incompatible empty-string form for both ALL baseline and UNSEEN polling searches.

The process-history window is an optional EMAIL_PP_PROCESS_HISTORY_WINDOW setting and matching platform extra. Positive values are seconds. Omitted or 0 means only unseen messages arriving after a cold connection are processed. -1 means every unseen message is processed. A positive value additionally processes unread messages whose IMAP INTERNALDATE is within the specified exact-second window. Automatic reconnects within one gateway process must preserve state and process unseen mail received during the outage, independent of the configured cold-start window.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both IMAP UID SEARCH calls pass None as the charset; a regression test reproduces a server where an empty-string charset returns no unseen messages.
- [x] #2 EMAIL_PP_PROCESS_HISTORY_WINDOW and process_history_window are exposed through the plugin manifest, Channels dashboard metadata, environment mapping, README, and validation.
- [x] #3 A missing or 0 process-history window preserves cold-start behavior by skipping messages already present before connection while processing unseen messages arriving afterward.
- [x] #4 A positive process-history window, expressed in seconds, processes only unseen cold-start messages whose IMAP INTERNALDATE is newer than the exact cutoff; malformed or absent INTERNALDATE values are skipped safely and reported.
- [x] #5 A process-history window of -1 processes all unseen messages in the selected mailbox; invalid non-integer values and values below -1 fail clearly.
- [x] #6 Eligible cold-start backlog is fetched oldest-first in bounded batches per poll, without loading the whole backlog into memory or starting unbounded agent work.
- [x] #7 Same-process automatic reconnects preserve mailbox state and process unseen messages received during the outage; UIDVALIDITY changes safely trigger cold-start history evaluation.
- [x] #8 Failed IMAP mailbox selection or search responses are reported as polling failures rather than silently treated as an empty inbox.
- [x] #9 Gateway logs include safe lifecycle, batch, poll, malformed-response, dispatch-failure, and debug-level authorization-rejection diagnostics without secrets, raw message bodies, or Authentication-Results contents.
- [x] #10 Automated tests cover every history mode, exact INTERNALDATE filtering, bounded ordering, new-mail handling, reconnect behavior, UIDVALIDITY changes, IMAP failures, and diagnostics; Ruff, format check, MyPy, and Pytest pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the adapter lifecycle, configuration surfaces, tests, and gateway logging interfaces.
2. Replace the cold-start UID baseline with validated IMAP mailbox state and bounded oldest-first unseen-history evaluation.
3. Preserve same-process reconnect state, detect UIDVALIDITY changes, and add safe lifecycle and diagnostic logging.
4. Expose and validate process_history_window across environment, plugin, dashboard metadata, and documentation.
5. Add focused regression tests for all history modes, failure paths, ordering, reconnects, and diagnostics; run Ruff, format, MyPy, and Pytest.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented validated process_history_window configuration and IMAP polling state keyed by mailbox. Cold starts store only the highest baseline UID; polling uses UID SEARCH with a None charset, fetches at most 25 messages per poll oldest-first, filters positive-history messages by parsed INTERNALDATE, and preserves state across matching-UIDVALIDITY reconnects. Added safe lifecycle, failure, malformed-response, dispatch, batch, and authorization diagnostics. Ruff, format, MyPy, and all task-relevant tests pass with 100% coverage. Full suite is blocked only by the pre-existing untracked .release-venv directory causing plugin_guard symlink-escape findings.

Human reviewed the implementation and approved marking TASK-006 done despite the workspace-local plugin-guard failure.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-08-26 18:10
---
Agent: Implementation is ready for review. The only remaining check is unrelated workspace contamination: plugin_guard scans the pre-existing untracked .release-venv and reports its external interpreter symlinks as critical.
---

author: @human
created: 2026-08-26 18:44
---
Human: Reviewed the implementation, approved marking TASK-006 done, and requested the 0.3.0 version bump.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented IMAP charset correction, controlled cold-start unread recovery, reconnect-safe mailbox state, configuration/documentation surfaces, and safe polling diagnostics. Verified with 16 focused adapter tests and 41 passing project tests at 100% coverage; Ruff, format, and MyPy pass. The remaining project test is the pre-existing plugin guard failure caused by the untracked .release-venv directory's external Python symlinks, so acceptance criterion 10 remains unchecked and the task stays In Progress for human review.
<!-- SECTION:FINAL_SUMMARY:END -->
