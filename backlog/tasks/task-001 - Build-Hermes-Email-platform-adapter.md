---
id: TASK-001
title: Build Hermes Email++ platform adapter
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-18 12:53'
updated_date: '2026-08-20 13:22'
labels: []
dependencies: []
references:
  - >-
    https://hermes-agent.nousresearch.com/docs/developer-guide/adding-platform-adapters
priority: high
type: feature
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deliver a third-party Hermes Agent platform plugin that connects through IMAP/SMTP while providing per-email-thread agent sessions, rich HTML email, configurable visible quoting, and a safe forwarded-message drafting workflow. The plugin must register as a distinct email_pp platform and remain independent from the built-in email adapter.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The pip-installed plugin registers a distinct email_pp Hermes platform without replacing the built-in email platform
- [x] #2 Messages from separate RFC email threads are handled in separate Hermes sessions, while replies and draft revisions remain in their originating sessions
- [x] #3 Outbound responses support safe multipart plain-text and HTML representations with configurable visible quoting
- [x] #4 English Gmail and Outlook inline forwards can be converted into review drafts without including the wrapper task prompt in the quoted original
- [x] #5 The adapter preserves appropriate IMAP/SMTP transport, access-control, sender-authentication, attachment, and loop-prevention behavior
- [x] #6 Installation, configuration, workflow behavior, limitations, and security considerations are documented
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Establish the pip-discoverable Email++ platform with isolated configuration.
2. Implement durable, per-thread email routing and secure IMAP/SMTP transport.
3. Add multipart rendering, configurable quoting, and forwarded-review drafts.
4. Document the operator contract and validate the built package and Hermes registry integration.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
All six implementation subtasks are complete. Final validation uses the published `hermes-agent>=0.19,<0.20` range rather than the previously referenced source commit; a clean wheel install with Hermes Agent 0.19.0 registered distinct `email` and `email_pp` entries. Full validation is recorded in TASK-001.06.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-08-18 12:55
---
Quoted responses should retain both visible quoted content and RFC In-Reply-To/References headers. The first release must support English Gmail and Outlook inline forwards, expose configurable quote behavior, and return forwarded-task results as separate draft emails rather than sending directly to the original correspondent.
---

author: Human
created: 2026-08-18 12:55
---
Ruff, MyPy, and Pytest must run for every implementation subtask. Distribution validation and the Hermes registration smoke test should be reserved for the final validation task.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Delivered the independent Email++ Hermes platform: isolated email_pp registration and configuration, durable per-RFC-thread routing, TLS IMAP/SMTP transport, safe multipart Markdown rendering with visible quote modes, fail-closed Gmail/Outlook forwarded-review drafts, and operator/security documentation. Validation passed Ruff, formatting, MyPy, 27 Pytest tests at 100% coverage, wheel/sdist inspection, and clean-wheel plugin discovery against published Hermes Agent 0.19.0. No ADRs or follow-up tasks were created.
<!-- SECTION:FINAL_SUMMARY:END -->
