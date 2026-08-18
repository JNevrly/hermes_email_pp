---
id: TASK-001.01
title: Establish the Email++ plugin foundation
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-18 12:53'
updated_date: '2026-08-18 13:18'
labels: []
dependencies: []
references:
  - >-
    https://hermes-agent.nousresearch.com/docs/developer-guide/adding-platform-adapters
  - >-
    https://github.com/NousResearch/hermes-agent/blob/e02d1e41fc6104187e20af9eac8b2820566e3508/hermes_cli/plugins.py
modified_files:
  - pyproject.toml
  - uv.lock
  - hermes_email_pp/__init__.py
  - hermes_email_pp/config.py
  - hermes_email_pp/plugin.py
  - hermes_email_pp/hermes_email_pp.py
  - tests/test_hermes_email_pp.py
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
- [x] #2 Registration exposes platform name email_pp and does not overwrite the built-in email registration
- [x] #3 Required and optional EMAIL_PP_* settings are validated and surfaced through the platform registration contract
- [x] #4 The plugin does not fall back to built-in EMAIL_* credentials or access-control settings
- [ ] #5 The package supports the Python versions supported by the targeted Hermes Agent release
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Ruff check and format check pass
- [x] #2 MyPy passes for the package
- [x] #3 Pytest passes with the configured coverage threshold
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Define the Hermes and Python compatibility range, add the email-pp `hermes_agent.plugins` entry point, and implement a lightweight registration module.
2. Define and validate the isolated `EMAIL_PP_*` configuration contract without reading built-in `EMAIL_*` variables.
3. Add registration/configuration tests, then run Ruff, MyPy, and Pytest with coverage.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Investigation: the project is a minimal Python 3.13 scaffold. Hermes discovers pip plugins through the hermes_agent.plugins entry-point group and platform plugins call ctx.register_platform(...). The entry module should remain import-light and use Platform('email_pp') so it cannot replace the built-in email enum registration.

Implemented the `email-pp` pip entry point and lightweight `email_pp` registration. The configuration contract permits only `EMAIL_PP_*` values or platform extras; it registers separate Email++ access-control env vars and does not inspect built-in email values. Python compatibility is declared as >=3.11,<3.14 and Hermes is pinned to the referenced 0.20.4 commit.

Validation passed: `.venv/bin/ruff check . && .venv/bin/ruff format --check .`, `.venv/bin/mypy hermes_email_pp`, and `.venv/bin/pytest --cov=hermes_email_pp tests/` (7 passed, 100% coverage). `uv lock` resolved Hermes 0.20.4 from the pinned commit. `uv sync --group dev` successfully built the editable package but exceeded the 300-second timeout while updating the Hermes Git source; installed-distribution and Hermes runtime smoke tests remain intentionally deferred to TASK-001.06 per the parent-task instruction.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-08-18 13:18
---
Agent: Ready for human review. Criteria 1 and 5 remain unchecked because installed-distribution validation and Hermes runtime smoke coverage are explicitly reserved for TASK-001.06.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Established the Email++ plugin foundation: a pip entry point registers distinct `email_pp`, configuration is isolated to `EMAIL_PP_*`, and the package targets Python 3.11-3.13 with the referenced Hermes 0.20.4 source. Ruff, MyPy, and Pytest passed (7 tests, 100% coverage). Installed-distribution and Hermes runtime smoke validation are deferred to TASK-001.06.
<!-- SECTION:FINAL_SUMMARY:END -->
