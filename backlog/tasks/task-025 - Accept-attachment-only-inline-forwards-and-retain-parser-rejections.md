---
id: TASK-025
title: Accept attachment-only inline forwards and retain parser rejections
status: Done
assignee:
  - '@opencode'
created_date: '2026-11-16T17:03:00Z'
updated_date: '2026-11-16T17:20:00Z'
labels: []
dependencies: []
priority: high
type: bug
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A privately supplied Outlook inline forward has a clear wrapper task and recognized original headers, but an empty original text body causes both MIME alternatives to be rejected despite a PDF attachment. The generic boundary warning misdiagnoses the failure, and successfully notifying the sender currently schedules permanent deletion. Keep the private correspondence and PDF out of repository fixtures; use sanitized generated messages for regression coverage.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The supplied attachment-only Outlook forward reaches the agent with its wrapper task and attachment available.
- [x] #2 Sanitized regression tests cover plain-text and HTML alternatives, including attachment-aware validation.
- [x] #3 An empty original body remains empty without injected placeholder text.
- [x] #4 Only the wrapper prompt is authorized instructions; forwarded material and attachments remain reference data.
- [x] #5 Missing wrapper tasks, required original headers, and ambiguous or nested boundaries fail closed even with attachments.
- [x] #6 Rejection diagnostics distinguish unsupported or incomplete content from boundary ambiguity.
- [x] #7 Parser-rejected mail remains recoverable and never enters successful-task expunge cleanup after a rejection notice.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm the private MIME sample locally and trace parser, cached attachment context, and deletion lifecycle.
2. Preserve the parse_forward optional-return API while adding explicit attachment context and structured failure diagnostics. Keep empty text empty and make attachment reference isolation explicit.
3. Use retained/seen handling for every parser rejection, independent of notice delivery, and add sanitized parser and adapter regression tests.
4. Replay both private alternatives and dispatch locally without exposing content; run coverage, lint, formatting, and type checks; record verified results for human review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Initial investigation: forwarding.py rejects any empty original_body; adapter._content already exposes cached attachment URLs before parsing. _dispatch treats successful unsafe-forward notice delivery as processed success and invokes _remember_processed_delivery, which schedules UID EXPUNGE. Existing _mark_seen retains terminal rejected mail and can be reused. Backlog CLI was absent from PATH; using /tmp/opencode/backlog. Existing TASK-10 ID collision is unrelated and was not modified.

Implemented explicit has_attachments parser context, ForwardFailure diagnostics with a backward-compatible parse_forward wrapper, and attachment-reference instruction isolation. Adapter passes cached media availability, logs content-free reason codes, sends specific notices, and marks parser rejections Seen before notifying without scheduling deletion. Sanitized regressions cover plain/HTML/multipart attachment-only forwards, missing structure with and without attachment context, all diagnostic categories, and retention after sent, unavailable-ID, or failed SMTP notices. Focused adapter tests: 86 passed. Ruff, format, and mypy pass. Full workspace run: 139 passed, 2 packaging tests blocked by pre-existing dangling .tox/py314 interpreter symlinks; coverage is 100%. Rechecking the full suite from a tracked-source snapshot excluding local build artifacts and private temp content.

Verification completed: both decoded private MIME alternatives now parse only when attachment context is supplied and retain original_body == empty string. Local dispatch of the unchanged private MIME message produced one agent event with the extracted wrapper prompt and cached PDF bytes matching the MIME attachment; persisted draft original_body stayed empty. Local private replay script: /tmp/opencode/replay_attachment_forward.py (not committed).
Full suite passed in a tracked-source snapshot: /workspaces/hermes_email_pp/.venv/bin/python -m pytest --cov=hermes_email_pp --cov-report=term-missing tests/ from /tmp/opencode/email_pp_forward_check_jzw70kv_: 141 passed, 100% coverage. The snapshot excludes private temp data and local build environments; creation helper is /tmp/opencode/snapshot_email_pp.py. Initial snapshot needed an identifier-safe directory name because the root directory-plugin __init__.py uses relative imports.
Workspace checks passed: uv run ruff check .; uv run ruff format --check .; uv run mypy hermes_email_pp; git diff --check. Workspace-only full-suite failures were existing dangling .tox/py314 interpreter links encountered by two source-copy packaging tests. No unrelated build artifacts were changed.
Ready for human review. Configured statuses are To Do, In Progress, and Done, with no review status; kept In Progress with the review label rather than marking the task accepted/Done. No ADR or follow-up development tasks required.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-11-16T17:03:00Z

---

Human: Fix valid attachment-only Outlook forwards, preserve fail-closed structural checks, provide accurate rejection diagnostics, and retain parser-rejected emails. Use the private temp email only for local verification; do not add it to the test suite.

---

author: Agent
created: 2026-11-16T17:10:00Z

---

Agent: Confirmed the private reproduction and successful body-line controls before changing code. The repaired adapter dispatches the unchanged private sample with its PDF intact and body empty. Parser failures now carry specific content-free diagnostics and are marked Seen before notice delivery without entering deletion cleanup. Ready for human review; final acceptance remains with the human.

---

author: Human
created: 2026-11-16T17:20:00Z

---

Human: Reviewed the fix and confirmed it is OK.

---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added explicit available-attachment context to strict forward parsing while preserving the optional-return parse_forward API. Empty attachment-bearing originals remain empty; only wrapper tasks are authorized, with forwarded text and attachments explicitly reference data. Added distinct unsupported-format, ambiguous-boundary, missing-task, incomplete-header, and missing-content diagnostics. Parser rejections are retained/marked Seen regardless of notice delivery and never queued for UID EXPUNGE. Updated README and sanitized regression tests; no private correspondence or PDF was added. Verified unchanged private MIME parsing and local event dispatch, 141 passing tests with 100% coverage from a clean tracked-source snapshot, Ruff lint/format, mypy, and diff checks. Workspace packaging tests encounter pre-existing broken .tox/py314 symlinks; clean-source packaging tests pass. Human review pending; no ADRs or follow-up tasks.

Human review completed and accepted on 2026-11-16; task moved to Done. This supersedes the review-pending statement above.
<!-- SECTION:FINAL_SUMMARY:END -->
