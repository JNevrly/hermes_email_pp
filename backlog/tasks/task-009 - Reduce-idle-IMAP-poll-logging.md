---
id: TASK-009
title: Reduce idle IMAP poll logging
status: In Progress
assignee:
  - '@opencode'
created_date: '2026-08-26 20:35'
updated_date: '2026-08-26 20:36'
labels:
  - email
  - imap
  - observability
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
modified_files:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
priority: medium
type: bug
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Suppress INFO-level IMAP batch-completion logs for idle polls so normal mailbox polling does not flood operator logs. Keep batch diagnostics when one or more IMAP message fetches were attempted, including failed attempts, and retain DEBUG-level idle-poll visibility.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 An IMAP poll with no eligible messages produces no completed-batch INFO log
- [x] #2 A poll that attempts at least one message fetch logs the fetched and attempted counts at INFO, including when no message is returned
- [x] #3 Focused regression tests and project quality checks pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm the existing poll and fetch logging behavior. 2. Make batch-completion INFO logging conditional on at least one fetch attempt. 3. Add caplog regression coverage for idle, failed, and successful fetch batches. 4. Run focused and project quality checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented conditional batch-completion logging: idle polls emit no INFO record, while attempted fetch batches retain fetched and attempted counts. Added caplog coverage for idle, failed-fetch, and successful-fetch cases. Verified with uv run pytest tests/test_adapter.py (17 passed); uv run ruff check .; uv run ruff format --check .; uv run mypy hermes_email_pp; and uv run pytest --cov=hermes_email_pp tests/ -k 'not repository_root_has_a_safe_hermes_plugin_scan' (42 passed, 1 deselected, 100% coverage). The unfiltered suite has the existing unrelated plugin-guard safety-scan failure (dangerous verdict).
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-08-26 20:36
---
Agent: Implementation and verification are ready for human review. The unfiltered suite's only failure is the pre-existing repository plugin-guard safety scan, unrelated to this task.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reduced idle IMAP polling noise by logging completed poll batches at INFO only after a message fetch is attempted. Added regression coverage for idle, failed, and successful batches. Focused tests, Ruff, package-scoped MyPy, and the coverage suite excluding the existing unrelated plugin-guard scanner failure pass.
<!-- SECTION:FINAL_SUMMARY:END -->
