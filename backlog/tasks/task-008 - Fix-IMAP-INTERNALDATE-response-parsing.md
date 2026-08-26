---
id: TASK-008
title: Fix IMAP INTERNALDATE response parsing
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-26 20:14'
updated_date: '2026-08-26 20:20'
labels: []
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
priority: high
type: bug
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Correct positive unread-history recovery for real imaplib UID FETCH responses where INTERNALDATE follows the RFC822 literal in a separate response element. Ship the correction as Email++ 0.3.1.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Positive history windows process eligible unread mail when INTERNALDATE follows the RFC822 literal
- [x] #2 Parser never treats raw message content as IMAP metadata and safely skips absent or malformed dates
- [x] #3 Realistic imaplib response-shape regression tests and release validation pass
- [x] #4 Canonical metadata, changelog, lockfile, and artifacts report 0.3.1
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Parse RFC822 literals and their IMAP metadata as separate response elements without examining raw message bytes.
2. Replace invalid test fixtures with realistic imaplib FETCH response sequences and cover trailing, leading, missing, and malformed INTERNALDATE values.
3. Run focused and release checks, then bump metadata and artifacts to 0.3.1 without tagging or publishing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated _fetch_message to locate the RFC822 literal, then inspect only that tuple header and trailing protocol bytes for INTERNALDATE. It never reads raw message bytes as metadata. Replaced the invalid combined-header fixtures with realistic imaplib response sequences and added a body containing a fake INTERNALDATE value to prove it is ignored. Verified uv lock --check, uv sync --group dev --locked, Ruff, format, MyPy, and 41 tests after installing the documented editable Hermes Agent checkout. Built /tmp/opencode/email-pp-0.3.1/hermes_email_pp-0.3.1.tar.gz and hermes_email_pp-0.3.1-py3-none-any.whl. The only deselected test remains the known workspace-local plugin_guard failure from the untracked .release-venv directory.

Human approved closure with the documented .release-venv plugin-guard exclusion.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-08-26 20:16
---
Agent: The 0.3.1 fix and artifacts are ready for human review; no tag or publication was requested.
---

author: @human
created: 2026-08-26 20:20
---
Human: Approved closing TASK-007 and TASK-008.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fixed real imaplib RFC822 literal response parsing and released version metadata as 0.3.1. Regression tests cover trailing INTERNALDATE metadata and date-like bytes inside an email body. Validation and artifacts are complete apart from the previously approved workspace-local plugin scanner exclusion. No tag, commit, or publication was created.
<!-- SECTION:FINAL_SUMMARY:END -->
