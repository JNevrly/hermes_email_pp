---
id: TASK-002
title: Automate tagged PyPI releases
status: In Progress
assignee:
  - '@opencode'
created_date: '2026-08-25 10:53'
updated_date: '2026-08-25 10:56'
labels: []
dependencies: []
references:
  - 'https://docs.pypi.org/trusted-publishers/using-a-publisher/'
  - 'https://github.com/pypa/gh-action-pypi-publish'
documentation:
  - README.md
modified_files:
  - .github/workflows/release.yml
  - README.md
priority: high
type: feature
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a GitHub Actions release pipeline that validates and publishes the package when a stable vX.Y.Z tag is pushed, creates a GitHub Release, and permits a manual bootstrap of an existing tag.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Pushing a stable vX.Y.Z tag runs a release workflow and rejects malformed tags
- [ ] #2 The workflow rejects a tag whose version does not equal pyproject.toml project.version
- [ ] #3 The workflow runs the existing lint, format, type, test, build, metadata, and installed-wheel checks before publication
- [ ] #4 The workflow publishes the built wheel and source distribution to PyPI using Trusted Publishing in the pypi environment
- [ ] #5 The workflow creates a generated-notes GitHub Release with the same distribution files only after PyPI publication succeeds
- [ ] #6 The workflow can be manually dispatched for an existing valid tag
- [ ] #7 README documents the version-tag release process and one-time Trusted Publisher setup
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a top-level GitHub Actions workflow for stable tag pushes and validated manual tag dispatches.
2. Verify the selected tag matches the package version, run the project checks, build and validate distributions, and share artifacts across isolated jobs.
3. Publish the verified artifacts through PyPI Trusted Publishing, then create a generated-notes GitHub Release with those artifacts.
4. Document the release procedure and one-time PyPI/GitHub setup.
5. Validate the workflow syntax and run the release checks locally.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added .github/workflows/release.yml with isolated build, PyPI Trusted Publishing, and GitHub Release jobs. The workflow validates stable tags against pyproject.toml, supports manual existing-tag dispatch, passes distributions through an artifact, and attaches them only after publication succeeds. README now documents the release process and required pending Trusted Publisher configuration.

Local validation passed: actionlint 1.7.12 accepted .github/workflows/release.yml; the tag guard accepted v0.1.0 and rejected malformed and mismatched versions; Ruff, format check, MyPy, 27 Pytest tests at 100% coverage, uv build, and twine metadata checks passed. An isolated Python 3.13 environment installed the wheel with Hermes Agent 0.19.0 and loaded the email-pp entry point. Remote PyPI publication and GitHub Release creation remain pending the maintainer's GitHub environment and PyPI pending Trusted Publisher configuration, then manual dispatch for v0.1.0.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-08-25 10:56
---
Human: Use PyPI Trusted Publishing, GitHub-generated release notes, and a manual existing-tag bootstrap for v0.1.0.
---
<!-- COMMENTS:END -->
