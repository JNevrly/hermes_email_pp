---
id: TASK-001.04
title: Add rich MIME rendering and configurable quoting
status: Done
assignee:
  - '@Josef'
created_date: '2026-08-18 12:54'
updated_date: '2026-08-18 14:32'
labels: []
dependencies:
  - TASK-001.03
references:
  - 'https://github.com/NousResearch/hermes-agent/issues/11941'
  - 'https://github.com/NousResearch/hermes-agent/pull/54107'
modified_files:
  - hermes_email_pp/adapter.py
  - hermes_email_pp/config.py
  - hermes_email_pp/rendering.py
  - pyproject.toml
  - uv.lock
  - tests/test_adapter.py
  - tests/test_hermes_email_pp.py
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
- [x] #1 Formatted responses are delivered as multipart/alternative with readable text/plain and safe text/html parts
- [x] #2 Messages with attachments have a valid multipart/mixed structure containing one multipart/alternative body followed by the attachments
- [x] #3 Markdown headings, emphasis, lists, links, tables, inline code, and fenced code render usefully in HTML-capable email clients
- [x] #4 Raw model HTML and quoted inbound content cannot inject active HTML, scripts, forms, remote resources, or unsafe link schemes
- [x] #5 EMAIL_PP_QUOTE_MODE accepts always, forwarded, and never, rejects invalid values, and defaults to always
- [x] #6 Ordinary quoted replies include both a visible clean quote and correct In-Reply-To and References headers
- [x] #7 Outbound subjects, display names, and non-ASCII address headers are encoded correctly using modern email APIs
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Ruff check and format check pass
- [x] #2 MyPy passes for the package
- [x] #3 Pytest passes with the configured coverage threshold
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a safe Markdown-to-HTML renderer and quote formatter that escapes untrusted content and allows only safe link schemes.
2. Build every body as multipart/alternative, promote attachment messages to multipart/mixed, and use EmailMessage header APIs.
3. Persist inbound plain-text quote and reference context; apply the configured always, forwarded, or never quote policy to replies.
4. Cover MIME shape, formatting, sanitization, quoting, configuration, headers, and attachments; run Ruff, MyPy, and coverage tests.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented a shared safe Markdown renderer using the Markdown tables and fenced-code extensions, then an HTML allowlist that retains only inert structural tags and http/https/mailto links. EmailMessage now emits multipart/alternative bodies and promotes attachment messages to multipart/mixed. Inbound plain text, sender, subject, and validated reference IDs are persisted as quote context; quote modes use that context and reserve forwarded-only quoting for Task-001.05 to mark. Verified with pytest --cov --cov-report=term-missing (23 passed, 100%), Ruff check/format, and MyPy.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @Josef
created: 2026-08-18 14:32
---
Human: Confirmed this subtask is done; README documentation remains scheduled for TASK-001.06.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented safe Markdown-rich multipart email construction with a shared renderer, standard-library EmailMessage headers, and MIME-safe attachments. Replies persist plain-text quote/reference context and honor EMAIL_PP_QUOTE_MODE (always, forwarded, never); forwarded-only quoting awaits Task-001.05 forward detection.

Verified: pytest --cov --cov-report=term-missing (23 passed, 100%); ruff check and format check; mypy hermes_email_pp; uv lock --check.

No ADRs or follow-up tasks created.
<!-- SECTION:FINAL_SUMMARY:END -->
