---
id: TASK-019
title: Configure Email++ outbound sender name
status: Done
assignee:
  - '@opencode'
created_date: '2026-09-04 07:18'
updated_date: '2026-09-04 07:24'
labels: []
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - hermes_email_pp/config.py
  - plugin.yaml
  - README.md
modified_files:
  - hermes_email_pp/config.py
  - hermes_email_pp/adapter.py
  - plugin.yaml
  - README.md
  - tests/test_hermes_email_pp.py
  - tests/test_adapter.py
priority: medium
type: feature
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a configurable display name for Email++ outgoing mail so recipients do not always see the hardcoded "Hermes Agent" sender name. The setting must follow existing Email++ configuration conventions and be editable in the Hermes Dashboard Channels card as well as supplied through environment or profile-scoped platform configuration. Retain "Hermes Agent" as the default when no custom name is configured.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 An optional Email++ sender-name setting is supported through the established environment and platform-extra configuration paths.
- [x] #2 The Hermes Dashboard Channels card exposes the sender-name setting with a clear label and description.
- [x] #3 Outgoing reply From headers use the configured sender display name while retaining EMAIL_PP_ADDRESS as the mailbox address.
- [x] #4 When the setting is empty or absent, outgoing replies retain the Hermes Agent display name.
- [x] #5 Documentation lists the setting, its default, and its purpose.
- [x] #6 Automated tests cover configured and default sender display names.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add EMAIL_PP_SENDER_NAME to the established environment, platform-extra, manifest, and Dashboard metadata registries.
2. Resolve the optional setting in EmailPPAdapter with Hermes Agent as its blank-value default, and use it in reply From headers.
3. Cover environment mapping plus configured/default outbound headers, document the setting, and run focused and full validation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added EMAIL_PP_SENDER_NAME with sender_name platform-extra mapping. Blank or absent values resolve to Hermes Agent; environment values take precedence. Dashboard metadata and plugin manifest expose the field.

Validated with .venv/bin/pytest --cov=hermes_email_pp tests/ (70 passed, 100% coverage), .venv/bin/ruff check ., .venv/bin/ruff format --check ., .venv/bin/mypy hermes_email_pp, git diff --check, and uv build --out-dir /tmp/opencode/email-pp-dist --clear.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-09-04 07:24
---
Agent: Implementation and verification are complete; task is ready for human review and acceptance.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented configurable Email++ outgoing sender display names through EMAIL_PP_SENDER_NAME and platform extra sender_name. Replies retain EMAIL_PP_ADDRESS while using the configured name; empty or absent configuration defaults to Hermes Agent.

Updated Dashboard metadata, plugin manifest, README settings documentation, and automated coverage for default/configured From headers plus environment mapping.

Verification: 70 tests passed with 100% coverage; Ruff lint/format, mypy, diff check, and package build all passed. No known limitations, follow-up tasks, or ADRs.
<!-- SECTION:FINAL_SUMMARY:END -->
