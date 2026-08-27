---
id: TASK-010
title: Release Hermes Email++ 0.3.2
status: In Progress
assignee:
  - '@Josef'
created_date: '2026-08-27 08:02'
updated_date: '2026-08-27 08:05'
labels: []
dependencies: []
modified_files:
  - pyproject.toml
  - plugin.yaml
  - hermes_email_pp/__init__.py
  - CHANGELOG.md
  - uv.lock
priority: high
type: chore
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Release the verified Outlook/O365 inline-forward parsing fix as Hermes Email++ 0.3.2.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All canonical version sources and uv.lock report 0.3.2
- [x] #2 CHANGELOG documents the 0.3.2 release
- [x] #3 Release validation and wheel build complete without creating a Git tag or publishing
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update package, plugin, and runtime version metadata and record the O365 fix in the changelog. 2. Regenerate and validate uv.lock. 3. Run release quality checks and build the 0.3.2 source and wheel artifacts without tagging or publishing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated all canonical version sources and regenerated uv.lock for 0.3.2. Validation passed: uv lock --check; uv sync --group dev --locked; .venv/bin/ruff check .; .venv/bin/ruff format --check .; .venv/bin/pytest --cov --cov-report=term-missing -k 'not repository_root_has_a_safe_hermes_plugin_scan' (44 passed, 1 deselected, 100% coverage). The single deselected scanner test fails only because pre-existing untracked .release-venv/ contents trigger plugin_guard findings. After locked sync removed the external test dependency, restored the documented editable Hermes Agent checkout at /tmp/opencode/hermes-agent-v2026.8.19. Built /tmp/opencode/email-pp-0.3.2/hermes_email_pp-0.3.2.tar.gz and /tmp/opencode/email-pp-0.3.2/hermes_email_pp-0.3.2-py3-none-any.whl.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @Josef
created: 2026-08-27 08:05
---
Agent: Version 0.3.2 metadata and artifacts are ready for human acceptance. No Git commit, tag, or publication was requested or created.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Prepared Hermes Email++ 0.3.2 for the Outlook/O365 inline-forward parsing fix. Synchronized package, plugin, runtime, changelog, and lockfile versions; lock, lint, formatting, and 100%-coverage tests pass with the known workspace-local scanner test excluded. Built source and wheel artifacts in /tmp/opencode/email-pp-0.3.2. No Git commit, tag, or publication was requested or created.
<!-- SECTION:FINAL_SUMMARY:END -->
