---
id: TASK-021
title: Allow Python 3.14 with an upper bound of 3.15
status: In Progress
assignee:
  - '@opencode'
created_date: '2026-10-24 16:53'
updated_date: '2026-10-24 16:57'
labels:
  - awaiting-human-review
dependencies: []
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Raise the supported Python range from >=3.11,<3.14 to >=3.11,<3.15 so installation permits the Python 3.14 runtime used by Hermes 0.22. The human approved updating metadata, regenerating uv.lock, adding Python 3.14 to tox, and running existing tests and quality checks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Project metadata and lockfile declare >=3.11,<3.15, and package classifiers include Python 3.14.
- [x] #2 Tox includes Python 3.14 and runs each test environment on its selected interpreter.
- [x] #3 Existing tests pass on Python 3.14 and existing lint, formatting, and type checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update requires-python and classifiers. 2. Add py314 to tox and ensure uv uses the tox environment interpreter. 3. Regenerate uv.lock without upgrading dependencies. 4. Run existing Python 3.13/3.14 tests and quality checks, then record evidence for human review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented >=3.11,<3.15 in pyproject.toml and uv.lock, added the Python 3.14 classifier, updated the existing metadata assertion, and added py314 to tox. All tox environments now inherit UV_PROJECT_ENVIRONMENT={envdir} so uv uses the selected interpreter rather than the shared .venv. Dependency versions are unchanged; lockfile additions are cp314/cp314t wheels.

Verification: uv lock --check passed. uv run tox -e lint passed Ruff, formatting (10 files), and MyPy (7 source files). Tox logs confirmed Python 3.13.15 and 3.14.7. Initial versioned tox test runs failed collection due to the undeclared Hermes test-host prerequisite. Installed editable /tmp/opencode/hermes-agent (0.20.5) into .tox/py313, then .tox/py313/bin/python -m pytest --cov=hermes_email_pp tests/ passed all 80 tests at 100% coverage.

For 3.14, the existing Hermes 0.20.5 host metadata itself excludes 3.14. Tested its source imports via PYTHONPATH instead, without modifying or overriding its package metadata: uv pip install --python .tox/py314/bin/python python-dotenv rich requests httpx pydantic; PYTHONPATH="/workspaces/hermes_email_pp:/tmp/opencode/hermes-agent" .tox/py314/bin/python -m pytest --cov=hermes_email_pp tests/ passed all 80 tests at 100% coverage. This verifies the plugin test suite on Python 3.14, not full Hermes 0.22 integration.

Known test-harness limitation: plain tox still needs a Hermes source host available after uv sync, as the host is intentionally not a plugin dependency. The shared development .venv Hermes host was restored after the first lint run removed its extraneous packages.

Ready for human review. No configured Review status exists (only To Do, In Progress, Done), so the task remains In Progress with awaiting-human-review label rather than being marked complete. No follow-up tasks or ADRs created.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-10-24 16:53
---
Human: Approved the proposed >=3.11,<3.15 range, Python 3.14 classifier, lockfile regeneration, and Python 3.14 tox checks.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Expanded Python compatibility to >=3.11,<3.15, added the 3.14 classifier and tox environment with interpreter isolation, regenerated the lockfile without dependency upgrades, and updated the existing metadata test. Verified all 80 tests on Python 3.13.15 and 3.14.7 with 100% coverage, plus lint/format/MyPy and lock consistency. Test-host setup and limits are documented in notes; full Hermes 0.22 integration was not exercised. Awaiting human acceptance.
<!-- SECTION:FINAL_SUMMARY:END -->
