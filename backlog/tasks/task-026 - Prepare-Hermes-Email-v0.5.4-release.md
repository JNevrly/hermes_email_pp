---
id: TASK-026
title: Prepare Hermes Email++ v0.5.4 release
status: Done
assignee:
  - '@opencode'
created_date: '2026-11-16T17:22:00Z'
updated_date: '2026-11-16T17:26:00Z'
labels: []
dependencies:
  - TASK-025
priority: medium
type: chore
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Prepare the reviewed attachment-only forward fix (TASK-025) as the next patch release. The human clarified that the requested version is v0.5.4 after learning v0.5.2 and v0.5.3 already exist. Scope is local release preparation and validated distribution artifacts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Project metadata, plugin manifest, package __version__, and editable lockfile entry consistently report 0.5.4.
- [x] #2 A dated v0.5.4 changelog entry describes attachment-only forward support, specific rejection diagnostics, and retained rejected emails.
- [x] #3 Locked dependency checks, metadata regression tests, quality checks, and release builds pass with results recorded.
- [x] #4 Wheel and source distribution artifacts for v0.5.4 are available locally and contain the reviewed fix without private correspondence.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Synchronize pyproject.toml, plugin.yaml, package __version__, and uv.lock to 0.5.4; add dated release notes for accepted TASK-025.
2. Preserve existing metadata-consistency tests; run uv lock --check, uv sync --group dev --locked, lint/format/type checks, and tests. Use a clean tracked-source snapshot for packaging tests to avoid existing dangling .tox interpreter links and private temp data.
3. Build wheel and sdist into /tmp/opencode/email-pp-0.5.4, validate distributions, and smoke-test the wheel in an isolated environment.
4. Record artifacts and verification in this task and hand off for human review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Loaded email-pp-version-bump skill. Current version is 0.5.3; tags v0.5.2 and v0.5.3 already exist. Existing tests assert pyproject/lock/package version agreement and plugin manifest/package agreement. The reviewed TASK-025 changes remain uncommitted in this working tree; existing untracked code_review_report.html is unrelated user work. Release workflow publishes on a pushed version tag, so preparation alone does not trigger it. No commit, tag, push, or publication has been requested.

Version sources now consistently report 0.5.4; uv.lock regenerated with only the editable project version changed. Added 2026-11-16 changelog notes for attachment-only forwards, specific diagnostics, and rejected-mail retention. Existing tests cover all four version sources. uv lock --check and uv sync --group dev --locked succeeded. Locked sync removed the separately installed Hermes test host as expected; reinstalled /tmp/opencode/hermes-agent (0.20.5) using uv pip install -e before checks. Ruff lint/format, mypy, and git diff --check pass. Full clean tracked-source suite from /tmp/opencode/email_pp_forward_check_tds3r950: 141 passed, 100% coverage. uv build produced wheel and sdist in /tmp/opencode/email-pp-0.5.4; distribution metadata and isolated wheel smoke checks are next.

Release verification complete: uv tool run twine check passed for the wheel and sdist. Installed the wheel into /tmp/opencode/email-pp-0.5.4/smoke, outside the checkout, and confirmed distribution/package version 0.5.4, plugin entry point loading, and attachment-aware empty-body parsing. /tmp/opencode/check_email_pp_release.py compared every packaged Python source in both archives byte-for-byte with the reviewed working tree and verified no .eml, .pdf, or temp directory is included. No private correspondence was used for release validation.
Artifacts: /tmp/opencode/email-pp-0.5.4/hermes_email_pp-0.5.4-py3-none-any.whl and /tmp/opencode/email-pp-0.5.4/hermes_email_pp-0.5.4.tar.gz.
Ready for human review. The board has no review status, so this task remains In Progress with a review label. No commit, tag, push, or publication performed. No new ADRs or follow-up tasks.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-11-16T17:22:00Z

---

Human: Confirmed v0.5.4 as the intended release version after initially requesting v0.5.2.

---

author: Agent
created: 2026-11-16T17:24:00Z

---

Agent: v0.5.4 metadata and changelog are ready. All 141 tests pass with 100% coverage in a clean tracked-source snapshot; quality, locked-dependency, distribution metadata, archive-content, and installed-wheel checks pass. Local artifacts are ready for review.

---

author: Human
created: 2026-11-16T17:26:00Z

---

Human: TASK-026 accepted.

---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Prepared v0.5.4 for the accepted attachment-only-forward fix: synchronized pyproject.toml, plugin.yaml, __version__, and uv.lock; added dated changelog notes. Existing consistency tests retained. Validated uv lock --check, locked development sync, Ruff lint/format, mypy, diff checks, and the full 141-test suite with 100% coverage from a clean tracked-source snapshot that avoids existing broken .tox interpreter links. Built wheel and sdist in /tmp/opencode/email-pp-0.5.4; Twine checks and isolated installed-wheel smoke tests pass. Both archives match the reviewed package source and contain no private email/PDF data. Ready for human review; no commit, version tag, or publication was requested or performed. No ADRs or follow-ups.

Human accepted TASK-026 on 2026-11-16; moved to Done. This supersedes the review-pending statement above.
<!-- SECTION:FINAL_SUMMARY:END -->
