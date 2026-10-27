---
id: TASK-024
title: Preserve angle-bracket Markdown link destinations in outbound HTML
status: Done
assignee:
  - '@OpenCode'
created_date: '2026-10-27T09:36:00Z'
updated_date: '2026-10-27T10:04:00Z'
labels: []
dependencies: []
references:
  - hermes_email_pp/rendering.py
modified_files:
  - hermes_email_pp/rendering.py
  - tests/test_rendering.py
  - tests/test_adapter.py
priority: high
type: bug
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PDF-signoff review links using valid [label](<URL>) syntax lose their href before SMTP delivery because render_markdown escapes the input before Markdown parsing. Fix labelled Markdown links while preserving the raw-HTML security boundary. Bare-URL autolinking is outside scope.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Ordinary and angle-bracket Markdown links are clickable for http, https, and mailto destinations, including the reported localhost review URL.
- [x] #2 Query parameters, ampersands, and percent-encoded tokens retain their original decoded destination, with valid HTML attribute escaping.
- [x] #3 Unsafe schemes remain blocked for both link syntaxes and untrusted inline/block raw HTML remains inert, including sanitizer-allowlisted tags.
- [x] #4 Regression tests cover both link forms, code escaping, and the generated outbound MIME HTML; lint, formatting, typing, and package coverage checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Disable Markdown raw-HTML block and inline processors, then parse unescaped Markdown and retain the existing HTML sanitizer.
2. Add direct regression cases for allowed and unsafe link forms, exact href preservation, raw HTML, and code escaping; extend outbound MIME coverage.
3. Run Ruff lint/format, MyPy, and the full coverage suite; record verified results for human review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation: render_markdown now creates a per-call Markdown instance, deregisters html_block and html processors, and converts unescaped Markdown. Markdown serializes raw HTML as escaped text; _SafeHTML remains unchanged, including its http/https/mailto allowlist. Added 27 direct renderer cases and an outbound MIME regression assertion.

Verification: Before the fix, direct tests reproduced four angle-bracket href failures (plus existing code double-escaping). After the fix all direct cases pass. Ruff lint/format, MyPy, and git diff --check pass. With the CI-pinned Hermes v2026.8.19 host (0.20.5), a clean source snapshot containing all current implementation/test changes passes all 107 tests at 100% package coverage.

Reproduction: installed the host from /tmp/opencode/hermes-agent using uv pip install -e; use uv run --no-sync to retain this undeclared test host. Workspace full run has 105 passes and two repository-copy failures caused by pre-existing dangling .tox/py314 Python symlinks. Clean snapshot at /tmp/opencode/email_pp_link_validation was exported from HEAD and patched with the working-tree changes and new test file; run there with PYTHONPATH=/tmp/opencode/email_pp_link_validation /workspaces/hermes_email_pp/.venv/bin/python -m pytest --cov=hermes_email_pp tests/. Keep snapshot directory names valid Python identifiers because root __init__.py is collected as a package.

Test fixture adjustment: use an inert file:///workspace/report.pdf URL for blocked file-scheme coverage; the initial sensitive-path fixture triggered the host plugin scanner. The final clean-snapshot scan and Git installer contract tests pass.

Review: project statuses currently offer only To Do, In Progress, and Done. Left In Progress with awaiting-review label for human acceptance. No product limitations, follow-up tasks, or ADRs. Backlog CLI is available at /tmp/opencode/backlog (standalone v1.55.3).

Human accepted the implementation on 2026-10-27 and requested closure. Task is now Done; the earlier review-pending note is superseded. Requested release preparation: synchronize version sources to 0.5.3, add a dated changelog entry, regenerate the lockfile, validate metadata, and build wheel/sdist artifacts.

Release preparation completed for human-requested patch 0.5.3: synchronized pyproject.toml, plugin.yaml, hermes_email_pp/__init__.py, and regenerated uv.lock; added CHANGELOG.md entry dated 2026-10-27. Old-version searches in TOML/YAML/Python found no remaining 0.5.2 metadata. uv lock --check and uv sync --group dev --locked passed; reinstalled the CI-pinned Hermes test host after sync. The updated clean source snapshot passes all 107 tests at 100% coverage, including existing version consistency tests. Ruff lint/format, MyPy, and diff checks pass. uv build produced /tmp/opencode/email-pp-0.5.3/hermes_email_pp-0.5.3.tar.gz and /tmp/opencode/email-pp-0.5.3/hermes_email_pp-0.5.3-py3-none-any.whl. No commit, Git tag, or publication performed.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @OpenCode
created: 2026-10-27T09:36:00Z

---

Human: Reported the angle-bracket link bug and approved the proposed renderer fix and regression-testing plan.

---

author: @OpenCode
created: 2026-10-27T09:56:00Z

---

Agent: Implementation and validation are ready for human review. All 107 tests pass in a clean source snapshot at 100% coverage; workspace-only failures are documented in the notes. The project has no configured review status, so the task remains In Progress with an awaiting-review label.

---

author: @OpenCode
created: 2026-10-27T10:03:00Z

---

Human: Reviewed the fix, said it looks good, explicitly requested closing the task and preparing a patch-version bump for release.

---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Human accepted the Markdown link fix on 2026-10-27. Fixed angle-bracket destinations by disabling raw-HTML parsing instead of pre-escaping all Markdown; existing sanitizer checks remain intact. Added 27 renderer regression cases and outbound MIME coverage. Verified 107 tests and 100% coverage in a clean source snapshot, plus Ruff lint/format, MyPy, and diff checks. Workspace-only repository-copy failures from dangling .tox symlinks remain documented. No follow-up tasks or ADRs.

Prepared patch release 0.5.3: synchronized package/plugin/runtime/lockfile versions and added dated changelog notes. Locked checks, lint/format/types, 107 tests at 100% coverage in a clean snapshot, and wheel/sdist builds passed. Artifacts are in /tmp/opencode/email-pp-0.5.3/. No commit, tag, or publication requested or performed.
<!-- SECTION:FINAL_SUMMARY:END -->
