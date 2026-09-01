---
id: TASK-016
title: Ignore release venv and scope coverage scans
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-29 00:00'
updated_date: '2026-09-01 06:32'
labels:
  - tooling
  - ci
dependencies: []
references:
  - .gitignore
  - pyproject.toml
priority: low
type: chore
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`.gitignore` ignores `.venv`, `venv/`, and `ENV/` but not `.release-venv/`, which sits in the working tree and could be committed accidentally. Task-010's notes also record a known full-suite failure where a `plugin_guard` scan picks up `.release-venv` contamination, and the coverage `omit = [".*", "*/site-packages/*"]` pattern does not clearly exclude a nested virtualenv. With `fail_under = 100` the suite is already strict, so this stray artifact makes CI brittle. Ignore the release virtualenv and scope the test/coverage configuration so a checked-in virtualenv can never be scanned.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `.release-venv/` (and comparable local build artifacts) are git-ignored
- [x] #2 Coverage/test configuration cannot scan a checked-in virtualenv such as `.release-venv`
- [x] #3 The full suite no longer fails due to `plugin_guard` scanning `.release-venv`
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add explicit `.release-venv/` ignores and pytest/coverage exclusions for local virtual environments.
2. Update the plugin-guard test to scan an installation-like staged tree that excludes local virtualenv directories.
3. Verify the scanner result and run formatting, linting, type checking, and the complete coverage suite.
4. If all checks pass, finalize TASK-016 and unblock/finalize TASK-014.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented an explicit .release-venv ignore, explicit coverage and pytest exclusions for local virtualenvs, and a shared staging exclusion list for plugin-scan and installer tests. The scanner test now mirrors an installed plugin tree rather than scanning local workspace artifacts. Validation passed: git check-ignore confirms .release-venv is ignored; focused scanner and installer tests passed; uv run pytest --cov=hermes_email_pp tests/ passed 58 tests at 100% coverage; Ruff lint and format checks and MyPy passed.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-09-01 06:32
---
Human: Requested TASK-016 and TASK-014 be closed once all tests pass.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Excluded local release virtualenvs from Git, pytest, coverage, plugin-guard staging, and installer-test staging. The full suite now passes with 58 tests and 100% coverage; Ruff and MyPy also pass.
<!-- SECTION:FINAL_SUMMARY:END -->
