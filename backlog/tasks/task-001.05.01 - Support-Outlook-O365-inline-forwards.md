---
id: TASK-001.05.01
title: Support Outlook O365 inline forwards
status: Done
assignee:
  - '@Josef'
created_date: '2026-08-27 04:26'
updated_date: '2026-08-27 08:02'
labels: []
dependencies: []
modified_files:
  - hermes_email_pp/forwarding.py
  - tests/test_adapter.py
  - README.md
parent_task_id: TASK-001.05
priority: high
type: bug
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Accept standard Outlook/O365 plain-text and HTML inline-forward boundaries while retaining strict prompt isolation and fail-closed behavior. The current parser rejects O365 messages that use a 32-underscore separator or the HTML hr/divRplyFwdMsg structure, including the reported O365 sample.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A complete Outlook/O365 plain-text forward using the exact 32-underscore separator creates a private review draft
- [x] #2 A complete HTML-only Outlook/O365 forward using its standard hr/divRplyFwdMsg structure creates a private review draft
- [x] #3 Only the wrapper prompt is passed as instructions and only the forwarded original is quoted in both draft alternatives
- [x] #4 Malformed, ambiguous, or nested supported forwarded boundaries fail closed without creating an agent task or draft
- [x] #5 Regression coverage includes multipart O365 content with an inline image and project documentation describes the supported forms
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add shared strict recognition for Outlook/O365 plain and HTML inline-forward boundaries, including structural HTML normalization that excludes styling content. 2. Preserve the existing prompt/header/body validation and reject multiple recognized boundaries. 3. Add end-to-end regression and fail-closed safety tests, update documentation, and run the project quality gate.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Confirmed against the private reported .eml: both decoded text/plain and text/html alternatives now parse successfully with the original Japanese subject. Full suite initially failed because the repository plugin scanner inspects the user-provided untracked temp/ sample and flags it as dangerous; no repository source issue was identified from that scanner result.

Correction: the plugin-scan failure is unrelated to temp/. It reports pre-existing untracked .release-venv/ external symlinks and installed package contents. The reported .eml remains uncommitted and parses successfully in both alternatives.

Validation passed: .venv/bin/ruff check hermes_email_pp tests; .venv/bin/ruff format --check hermes_email_pp tests; .venv/bin/mypy hermes_email_pp; .venv/bin/pytest --cov --cov-report=term-missing -k 'not repository_root_has_a_safe_hermes_plugin_scan' (44 passed, 1 deselected, 100% coverage). The full unfiltered suite has one unrelated failure: the plugin scan sees untracked .release-venv/ external symlinks and installed packages.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @Josef
created: 2026-08-27 04:30
---
Agent: Implementation and verification are complete and ready for human review. The configured statuses have no review state, so the task remains In Progress for human acceptance.
---

author: @Josef
created: 2026-08-27 08:02
---
Human: Approved closing this verified task and requested the 0.3.2 release.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added strict Outlook/O365 support for the exact 32-underscore text separator and divRplyFwdMsg HTML header structure. The normalizer excludes head/style/script content and preserves a canonical header/body boundary. Parsing now rejects multiple supported boundaries to fail closed for nested forwards. Added end-to-end plain, HTML-only multipart-with-inline-image, prompt-isolation, and fail-closed regressions; documented the supported formats. Verified the private reported sample parses in both alternatives. Quality checks pass; the only unfiltered-suite failure is an unrelated pre-existing .release-venv plugin-scan finding. No ADRs or follow-up tasks.
<!-- SECTION:FINAL_SUMMARY:END -->
