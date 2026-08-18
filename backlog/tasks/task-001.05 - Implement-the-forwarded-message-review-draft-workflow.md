---
id: TASK-001.05
title: Implement the forwarded-message review-draft workflow
status: To Do
assignee: []
created_date: '2026-08-18 12:54'
labels: []
dependencies:
  - TASK-001.04
references:
  - 'https://github.com/felipehertzer/email-forward-parser-py'
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
- [ ] #1 English Gmail and Outlook inline forwards are recognized from both text/plain and text/html alternatives using representative fixtures
- [ ] #2 A recognized forward yields separate task-prompt, original-message metadata, and original-message body values
- [ ] #3 Hermes receives explicit per-event guidance to treat only the wrapper prompt as instructions and the forwarded message as reference data
- [ ] #4 The first result is sent to the authorized user as a fresh email with subject Draft: Re: <original subject> and without wrapper-thread In-Reply-To or References headers
- [ ] #5 The review draft contains the Hermes response plus a quote of only the forwarded original; the wrapper task prompt is absent from the quote in both plain and HTML parts
- [ ] #6 Replying to a generated draft returns to the originating Hermes session, and subsequent revisions can remain in the draft email thread
- [ ] #7 The adapter never sends a draft directly to the original correspondent
- [ ] #8 Suspected forwards with no reliable prompt/original boundary fail closed with a clear response and do not produce a potentially leaking quote
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Ruff check and format check pass
- [ ] #2 MyPy passes for the package
- [ ] #3 Pytest passes with the configured coverage threshold
<!-- DOD:END -->
