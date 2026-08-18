---
id: TASK-001
title: Build Hermes Email++ platform adapter
status: To Do
assignee: []
created_date: '2026-08-18 12:53'
updated_date: '2026-08-18 12:55'
labels: []
dependencies: []
references:
  - >-
    https://github.com/NousResearch/hermes-agent/blob/e02d1e41fc6104187e20af9eac8b2820566e3508/plugins/platforms/email/adapter.py
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
- [ ] #1 The pip-installed plugin registers a distinct email_pp Hermes platform without replacing the built-in email platform
- [ ] #2 Messages from separate RFC email threads are handled in separate Hermes sessions, while replies and draft revisions remain in their originating sessions
- [ ] #3 Outbound responses support safe multipart plain-text and HTML representations with configurable visible quoting
- [ ] #4 English Gmail and Outlook inline forwards can be converted into review drafts without including the wrapper task prompt in the quoted original
- [ ] #5 The adapter preserves appropriate IMAP/SMTP transport, access-control, sender-authentication, attachment, and loop-prevention behavior
- [ ] #6 Installation, configuration, workflow behavior, limitations, and security considerations are documented
<!-- AC:END -->

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
