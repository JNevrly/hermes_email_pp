---
id: TASK-023
title: Use minimum dependency versions without speculative upper bounds
status: In Progress
assignee:
  - '@opencode'
created_date: '2026-10-24 17:54'
updated_date: '2026-10-24 17:58'
labels:
  - awaiting-human-review
dependencies: []
references:
  - docs/adr/0001-use-minimum-dependency-versions.md
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The human reports Hermes requires ruff==0.15.10 and wants to avoid repeated compatibility edits when upgrading Hermes. Declare Python >=3.13 and Ruff >=0.14.0, and remove other unjustified upper bounds. Keep exact resolved development versions in uv.lock for repeatable checks, and retain the current release-host validation baseline.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Python metadata requires >=3.13 without an upper bound, with matching supported-version classifiers and Ruff target.
- [x] #2 Runtime and development requirements use lower bounds where no concrete incompatibility justifies a ceiling; Ruff 0.15.10 satisfies the declared requirement.
- [x] #3 Lockfile is current and existing lint, formatting, typing, and test checks pass on Python 3.13 and 3.14.
- [x] #4 Document the dependency policy, the role of uv.lock, and any justified exceptions.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect declared requirements and dependency API use. 2. Remove the Python ceiling, set minimum 3.13, drop obsolete classifiers, and align Ruff target. 3. Remove speculative runtime/dev ceilings; update existing metadata assertions and document policy in README/ADR. 4. Regenerate the lockfile with Ruff 0.15.10 while retaining other compatible locked versions. 5. Run existing quality checks and tests on both supported interpreters; record evidence for human review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Inspection: Markdown is the sole runtime dependency and rendering.py uses its public markdown() entry point plus tables/fenced_code extensions; no known incompatibility justifies its <4 ceiling. All remaining ceilings are development tooling major-version caps, with no documented incompatibility. Build backend already has only a lower bound. Ruff is a dev-only requirement, not a wheel runtime requirement. Existing metadata tests assert exact Python and Markdown requirement strings and must be updated. No docs/adr directory or repository ADR template currently exists; use a concise standard ADR for this long-lived dependency policy.

Implemented lower-only requirements for Python, Markdown, tox, coverage, Ruff, pytest, pytest-cov, PyYAML, and MyPy. Removed Python 3.11/3.12 classifiers and aligned Ruff target to py313. Updated existing metadata assertions, README, and proposed ADR 0001. uv lock --upgrade-package ruff==0.15.10 succeeded: Ruff is now locked to the Hermes-requested 0.15.10, other retained packages stayed at their versions, and tomli was removed because Python 3.11 is no longer supported. Python 3.15 resolution markers in uv.lock belong to dependency resolution, not a project Python ceiling. Initial Ruff 0.15.10 lint/format and MyPy pass on Python 3.13; both environments have synced successfully.

Final verification: uv lock --check passed and locked dev sync succeeded in both .venv (Python 3.13.15) and .tox/py314 (Python 3.14.7). Ruff --version reports 0.15.10 in both; lint and format checks pass on all 10 files, and MyPy passes on 7 source files in each environment. Existing pytest suite passes all 80 tests at 100% coverage on each interpreter. git diff --check passed.

Commands: .venv/bin/ruff check .; .venv/bin/ruff format --check .; .venv/bin/mypy hermes_email_pp; .venv/bin/python -m pytest --cov=hermes_email_pp tests/. Python 3.14 equivalents use .tox/py314/bin and test PYTHONPATH="/workspaces/hermes_email_pp:/tmp/opencode/hermes-agent".

Test-host context remains the previous validation baseline: editable Hermes 0.20.5 on 3.13; the same source exposed through PYTHONPATH with its needed import dependencies on 3.14, since that host package metadata excludes 3.14. This verifies plugin tests and Ruff compatibility, not full Hermes 0.22 integration or untested future dependencies. No dependency cap exceptions were needed; CI still explicitly selects 3.13 for its existing host.

Architecture: docs/adr/0001-use-minimum-dependency-versions.md records the proposed long-lived policy, alternatives, and lockfile trade-off. README summarizes it. Version remains 0.5.1; no release was requested. No follow-up tasks, commits, tags, pushes, or publications were performed. Ready for human review; kept In Progress with awaiting-human-review because no Review status exists.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-10-24 17:54
---
Human: Hermes now requires ruff==0.15.10. Wants to avoid recurring dependency conflicts on Hermes upgrades by using Python >=3.13, Ruff >=0.14.0, and removing upper caps wherever reasonable.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Changed Python to >=3.13 and removed speculative upper bounds from Markdown and all development requirements, including Ruff >=0.14.0. Aligned classifiers and Ruff target with the new minimum, updated existing metadata assertions, regenerated uv.lock with Ruff 0.15.10, and documented the dependency policy in README and proposed ADR 0001. Verified locked sync/lock consistency, lint/format/types, and all 80 tests with 100% coverage on Python 3.13.15 and 3.14.7. Existing Hermes test-host limitations remain documented; awaiting human acceptance.
<!-- SECTION:FINAL_SUMMARY:END -->
