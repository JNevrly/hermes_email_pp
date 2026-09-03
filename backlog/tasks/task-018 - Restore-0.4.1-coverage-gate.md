---
id: TASK-018
title: Restore 0.4.1 coverage gate
status: Done
assignee:
  - '@opencode'
created_date: '2026-09-03 17:39'
updated_date: '2026-09-03 17:42'
labels: []
dependencies: []
modified_files:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The v0.4.1 release CI has 68 passing tests but four uncovered statements in hermes_email_pp/adapter.py, causing its required 100% coverage gate to fail.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The test suite covers every executable statement counted in hermes_email_pp
- [x] #2 The configured coverage report reaches the required 100% threshold
- [x] #3 Release CI quality commands complete successfully
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Mark the defensive post-retry assertion as excluded because the fixed two-attempt loop cannot reach it.
2. Add a focused IMAP authentication-failure test that verifies the temporary client is closed and the original exception propagates.
3. Run the release workflow quality commands with Hermes Agent v2026.8.19 installed and record the results.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reproduced the release workflow locally after installing Hermes Agent v2026.8.19. Coverage identifies adapter.py lines 511 and 518-520 as the four misses: line 511 is unreachable after the fixed two-iteration retry loop; lines 518-520 are the login-failure cleanup path.

Validation passed with Hermes Agent v2026.8.19: uv run ruff check .; uv run ruff format --check .; uv run mypy hermes_email_pp; uv run pytest --cov=hermes_email_pp tests/ (69 passed, 100.00% coverage).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Excluded the unreachable post-retry assertion from coverage and added an IMAP login-failure cleanup regression test. Verified all release quality checks with Hermes Agent v2026.8.19; pytest reports 69 passed and 100.00% coverage. No known limitations, follow-up tasks, or ADRs.
<!-- SECTION:FINAL_SUMMARY:END -->
