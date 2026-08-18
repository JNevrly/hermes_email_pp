---
id: TASK-001.01
title: Establish the Email++ plugin foundation
status: To Do
assignee: []
created_date: '2026-08-18 12:53'
labels: []
dependencies: []
references:
  - >-
    https://hermes-agent.nousresearch.com/docs/developer-guide/adding-platform-adapters
  - >-
    https://github.com/NousResearch/hermes-agent/blob/e02d1e41fc6104187e20af9eac8b2820566e3508/hermes_cli/plugins.py
parent_task_id: TASK-001
priority: high
type: task
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn the package scaffold into a pip-discoverable Hermes platform plugin named email-pp that registers the distinct email_pp platform. Define the supported Hermes/Python compatibility range and an isolated EMAIL_PP_* configuration surface so enabling Email++ cannot accidentally enable or share configuration with the built-in email adapter.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Installing the package exposes the email-pp entry point in the hermes_agent.plugins group
- [ ] #2 Registration exposes platform name email_pp and does not overwrite the built-in email registration
- [ ] #3 Required and optional EMAIL_PP_* settings are validated and surfaced through the platform registration contract
- [ ] #4 The plugin does not fall back to built-in EMAIL_* credentials or access-control settings
- [ ] #5 The package supports the Python versions supported by the targeted Hermes Agent release
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Ruff check and format check pass
- [ ] #2 MyPy passes for the package
- [ ] #3 Pytest passes with the configured coverage threshold
<!-- DOD:END -->
