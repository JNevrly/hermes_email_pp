---
id: TASK-001.06
title: Document and validate the complete Email++ plugin
status: To Do
assignee: []
created_date: '2026-08-18 12:54'
labels: []
dependencies:
  - TASK-001.05
references:
  - README.md
  - 'https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins'
parent_task_id: TASK-001
priority: high
type: task
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Finish the feature with operator documentation and end-to-end release validation after all implementation tasks are complete. Validate the built artifacts and prove that a clean Hermes Agent installation discovers and registers email_pp without disturbing the built-in email platform.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 README documents installation into the Hermes environment, plugin enablement, all EMAIL_PP_* settings, quote modes, and disabling the built-in adapter for a shared mailbox
- [ ] #2 README documents ordinary replies, separate forwarded review drafts, draft revision behavior, supported Gmail and Outlook formats, parsing limitations, and fail-closed behavior
- [ ] #3 README documents credential storage, allowlisting, sender authentication, attachment handling, local context persistence, and mailbox security recommendations
- [ ] #4 Distribution artifacts build successfully and their metadata, package contents, and entry point are validated
- [ ] #5 In a clean environment with the targeted Hermes Agent version, plugin discovery loads email-pp and the platform registry contains both email and email_pp as distinct registrations
- [ ] #6 The final full test suite covers plugin registration, thread isolation, restart persistence, transport security, MIME structure, quote modes, forward parsing, prompt exclusion, draft delivery, and draft revision continuity
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Ruff check and format check pass
- [ ] #2 MyPy passes for the package
- [ ] #3 Pytest passes with the configured coverage threshold
- [ ] #4 Package build and artifact validation pass after the implementation checks
- [ ] #5 Hermes registration smoke test passes as the final verification step
<!-- DOD:END -->
