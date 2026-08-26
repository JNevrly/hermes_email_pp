---
id: TASK-005
title: Recover locked release build for 0.2.3
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-26 12:48'
updated_date: '2026-08-26 12:52'
labels: []
dependencies: []
references:
  - .github/workflows/release.yml
  - .opencode/skills/email-pp-version-bump/SKILL.md
modified_files:
  - pyproject.toml
  - uv.lock
  - plugin.yaml
  - hermes_email_pp/__init__.py
  - CHANGELOG.md
  - tests/test_hermes_email_pp.py
  - README.md
  - .opencode/skills/email-pp-version-bump/SKILL.md
priority: high
type: bug
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Release validation fails because prior 0.2.1 and 0.2.2 version bumps changed project metadata without regenerating uv.lock. Ship a new immutable 0.2.3 release with synchronized version metadata and a verified lockfile; preserve the existing release tags.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All current package-version sources and the editable package entry in uv.lock declare 0.2.3
- [x] #2 uv lock --check and uv sync --group dev --locked succeed
- [x] #3 A regression test detects disagreement between pyproject.toml and the root package entry in uv.lock
- [x] #4 Version-bump and release documentation require regenerating and verifying uv.lock before tagging
- [x] #5 Release-quality lint, format, type, test, build, and distribution metadata checks pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update all 0.2.2 release metadata to 0.2.3 and regenerate uv.lock without dependency upgrades. 2. Extend version-consistency coverage to verify the local package entry in uv.lock. 3. Document the lockfile requirement in the version-bump skill and release instructions. 4. Run the locked sync and release validation checks, then move the task to review for human acceptance.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Confirmed locally: pyproject.toml and package metadata declare 0.2.2, while uv.lock's editable hermes-email-pp entry declares 0.2.0. uv lock --check fails and uv lock --dry-run proposes only the local package version update. Existing v0.2.1 and v0.2.2 tags are preserved; PyPI has no 0.2.1 or 0.2.2 distributions.

Updated pyproject.toml, plugin.yaml, hermes_email_pp.__version__, and CHANGELOG.md to 0.2.3. Ran uv lock; its only lockfile change is the editable hermes-email-pp entry from 0.2.0 to 0.2.3.

uv lock --check and uv sync --group dev --locked now succeed. Focused tests initially could not import yaml after sync because yaml is supplied by the workflow's editable Hermes Agent test host; cloned the workflow-pinned Hermes v2026.8.19 tag and installed it with uv pip install -e before release validation.

Extended the version-consistency test to parse uv.lock and assert the editable package version matches hermes_email_pp.__version__. Documented uv lock regeneration plus locked verification in the project version-bump skill and README release procedure. Added coverage for the existing fallback when Hermes lacks Channels metadata, which the workflow-pinned Hermes version exposed as previously untested.

Final verification: uv lock --check; uv sync --group dev --locked; Ruff check and format check; MyPy; 39 Pytest tests at 100% coverage with the workflow-pinned Hermes v2026.8.19 host; uv build; Twine metadata validation; and an isolated installed-wheel entry-point smoke test all passed. No Git tag was created and no publication was attempted.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Recovered release validation for a new 0.2.3 release by synchronizing all version metadata and the editable uv.lock package entry. Added regression tests for lockfile-version drift and the Hermes-metadata fallback, and documented lock regeneration plus locked verification before tagging. Verified locked sync, Ruff, MyPy, 39 tests at 100% coverage, build, Twine, and installed-wheel smoke test. Existing v0.2.1 and v0.2.2 tags were preserved; no tag, publication, ADR, or follow-up task was created.
<!-- SECTION:FINAL_SUMMARY:END -->
