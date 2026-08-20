---
id: TASK-001.05
title: Implement the forwarded-message review-draft workflow
status: Done
assignee:
  - '@Josef'
created_date: '2026-08-18 12:54'
updated_date: '2026-08-20 11:21'
labels: []
dependencies:
  - TASK-001.04
references:
  - 'https://github.com/felipehertzer/email-forward-parser-py'
modified_files:
  - hermes_email_pp/adapter.py
  - hermes_email_pp/forwarding.py
  - tests/test_adapter.py
parent_task_id: TASK-001
priority: high
type: feature
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Recognize English Gmail and Outlook inline forwards, separate the authorized user task prompt from the forwarded original, and have Hermes return a send-ready review draft in a fresh email. Preserve the original forwarded content as reference data and visible quote material while ensuring the private wrapper prompt is not copied into that quote.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 English Gmail and Outlook inline forwards are recognized from both text/plain and text/html alternatives using representative fixtures
- [x] #2 A recognized forward yields separate task-prompt, original-message metadata, and original-message body values
- [x] #3 Hermes receives explicit per-event guidance to treat only the wrapper prompt as instructions and the forwarded message as reference data
- [x] #4 The first result is sent to the authorized user as a fresh email with subject Draft: Re: <original subject> and without wrapper-thread In-Reply-To or References headers
- [x] #5 The review draft contains the Hermes response plus a quote of only the forwarded original; the wrapper task prompt is absent from the quote in both plain and HTML parts
- [x] #6 Replying to a generated draft returns to the originating Hermes session, and subsequent revisions can remain in the draft email thread
- [x] #7 The adapter never sends a draft directly to the original correspondent
- [x] #8 Suspected forwards with no reliable prompt/original boundary fail closed with a clear response and do not produce a potentially leaking quote
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Ruff check and format check pass
- [x] #2 MyPy passes for the package
- [x] #3 Pytest passes with the configured coverage threshold
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Parse each inbound message's text/plain and text/html alternatives for unambiguous English Gmail or Outlook inline-forward boundaries.
2. Persist the wrapper task, forwarded metadata, and isolated forwarded quote source; send Hermes only the wrapper prompt with explicit reference-data guidance.
3. Deliver the initial response as a fresh, authorized-user-only draft with a forwarded-original quote, then retain aliases so draft replies return to the same Hermes session.
4. Add representative MIME fixtures and transport assertions, then run Ruff, MyPy, and coverage tests.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented strict dependency-free Gmail/Outlook forward parsing with prompt isolation, private fresh-draft delivery, outbound draft aliases, and fail-closed notices. Focused adapter tests pass.

Validation passed: .venv/bin/ruff check hermes_email_pp tests; .venv/bin/ruff format --check hermes_email_pp tests; .venv/bin/mypy hermes_email_pp; .venv/bin/pytest --cov --cov-report=term-missing (27 passed, 100% coverage).
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @Josef
created: 2026-08-20 10:36
---
Agent: Implementation and verification are complete and ready for human review. The configured statuses offer no review state, so the task remains In Progress rather than being marked Done.
---

author: @Josef
created: 2026-08-20 11:21
---
Human: Reviewed the implementation and approved closing this task.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented strict Gmail/Outlook inline-forward parsing and HTML normalization without adding a dependency. Hermes receives an explicit task/reference boundary; first replies are private, unthreaded Draft: Re: <original subject> emails that quote only the original. Outbound aliases keep draft revisions in the same Hermes session, and ambiguous forwards receive a safe, unquoted failure notice. Verified with Ruff, MyPy, and 27 passing pytest cases at 100% coverage. No ADRs or follow-up tasks.
<!-- SECTION:FINAL_SUMMARY:END -->
