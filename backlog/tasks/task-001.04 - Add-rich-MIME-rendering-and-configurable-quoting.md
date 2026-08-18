---
id: TASK-001.04
title: Add rich MIME rendering and configurable quoting
status: To Do
assignee: []
created_date: '2026-08-18 12:54'
labels: []
dependencies:
  - TASK-001.03
references:
  - 'https://github.com/NousResearch/hermes-agent/issues/11941'
  - 'https://github.com/NousResearch/hermes-agent/pull/54107'
parent_task_id: TASK-001
priority: high
type: task
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Produce modern email messages with safe rich formatting and conventional visible quote blocks while retaining readable plain-text alternatives and RFC client threading. Apply one consistent body and attachment construction policy across direct replies, media/document delivery, and standalone sends.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Formatted responses are delivered as multipart/alternative with readable text/plain and safe text/html parts
- [ ] #2 Messages with attachments have a valid multipart/mixed structure containing one multipart/alternative body followed by the attachments
- [ ] #3 Markdown headings, emphasis, lists, links, tables, inline code, and fenced code render usefully in HTML-capable email clients
- [ ] #4 Raw model HTML and quoted inbound content cannot inject active HTML, scripts, forms, remote resources, or unsafe link schemes
- [ ] #5 EMAIL_PP_QUOTE_MODE accepts always, forwarded, and never, rejects invalid values, and defaults to always
- [ ] #6 Ordinary quoted replies include both a visible clean quote and correct In-Reply-To and References headers
- [ ] #7 Outbound subjects, display names, and non-ASCII address headers are encoded correctly using modern email APIs
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Ruff check and format check pass
- [ ] #2 MyPy passes for the package
- [ ] #3 Pytest passes with the configured coverage threshold
<!-- DOD:END -->
