---
id: TASK-007
title: Bump Email++ to 0.3.0
status: In Progress
assignee:
  - '@opencode'
created_date: '2026-08-26 18:44'
updated_date: '2026-08-26 18:46'
labels: []
dependencies: []
priority: high
type: chore
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Release the reviewed IMAP polling and unread-history recovery changes as Hermes Email++ 0.3.0.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All canonical version sources and uv.lock report 0.3.0
- [x] #2 CHANGELOG documents the 0.3.0 release
- [ ] #3 Release validation and wheel build complete
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update canonical package, plugin, and runtime version metadata plus the changelog.
2. Regenerate and verify uv.lock.
3. Run release validation and build a 0.3.0 artifact without tagging or publishing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated pyproject.toml, plugin.yaml, hermes_email_pp/__init__.py, CHANGELOG.md, and regenerated uv.lock for 0.3.0. Added PyYAML as the direct pinned dev dependency required by tests/test_hermes_email_pp.py so uv sync --group dev --locked can collect the suite. Verified uv lock --check, uv sync --group dev --locked, Ruff, and 25 integration tests after installing the documented editable Hermes Agent checkout. Built hermes_email_pp-0.3.0.tar.gz and hermes_email_pp-0.3.0-py3-none-any.whl in /tmp/opencode/email-pp-0.3.0. The scanner test remains excluded because the pre-existing untracked .release-venv triggers plugin_guard symlink-escape findings.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-08-26 18:46
---
Agent: Version 0.3.0 artifacts are built and ready for review. No tag, commit, or publication was created.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Bumped Hermes Email++ to 0.3.0, regenerated the lockfile, documented the release, and built source and wheel artifacts. No Git tag or publication was requested. Release validation is pending human acceptance of the known workspace-local plugin-guard exclusion.
<!-- SECTION:FINAL_SUMMARY:END -->
