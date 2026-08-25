---
id: TASK-002
title: Automate tagged PyPI releases
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-25 10:53'
updated_date: '2026-08-25 11:28'
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
  - hermes_email_pp/threading.py
  - pyproject.toml
  - uv.lock
  - CHANGELOG.md
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
- [x] #1 Pushing a stable vX.Y.Z tag runs a release workflow and rejects malformed tags
- [x] #2 The workflow rejects a tag whose version does not equal pyproject.toml project.version
- [x] #3 The workflow runs the existing lint, format, type, test, build, metadata, and installed-wheel checks before publication
- [x] #4 The workflow publishes the built wheel and source distribution to PyPI using Trusted Publishing in the pypi environment
- [x] #5 The workflow creates a generated-notes GitHub Release with the same distribution files only after PyPI publication succeeds
- [x] #6 The workflow can be manually dispatched for an existing valid tag
- [x] #7 README documents the version-tag release process and one-time Trusted Publisher setup
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a top-level GitHub Actions workflow for stable tag pushes and validated manual tag dispatches.
2. Verify the selected tag matches the package version, run the project checks, build and validate distributions, and share artifacts across isolated jobs.
3. Publish the verified artifacts through PyPI Trusted Publishing, then create a generated-notes GitHub Release with those artifacts.
4. Document the release procedure and one-time PyPI/GitHub setup.
5. Validate the workflow syntax and run the release checks locally.

6. Bump the unreleased package and changelog version to 0.1.1 so the first public artifact corresponds to a new immutable v0.1.1 tag.

7. Check out the verified tag in the GitHub Release job and add a documented manual recovery input that skips PyPI only after a version has already been published.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Release workflow: .github/workflows/release.yml isolates build/test, PyPI Trusted Publishing, and GitHub Release creation. It validates stable tags against pyproject.toml, passes exact artifacts between jobs, and generates GitHub release notes.

CI fix: hermes_constants is optional but GitHub's clean environment exposes it as an installed untyped module. The import suppresses both import-not-found and import-untyped; its line-local Ruff I001 suppression keeps the MyPy-required statement-level ignore.

Release target: preserve the existing unpublished v0.1.0 tag. The first public release is 0.1.1/v0.1.1; pyproject.toml and uv.lock were bumped, the changelog records the first PyPI release, and the README no longer suggests bootstrapping v0.1.0.

Recovery: the GitHub Release job checks out the verified tag before gh release create --verify-tag. workflow_dispatch has skip_pypi (default false), which skips only the upload step when the exact version already exists on PyPI.

Verification: actionlint 1.7.12 accepted the workflow. Ruff, format check, clean MyPy (--no-incremental), 27 Pytest tests at 100% coverage, uv lock --check, uv build, twine metadata validation, and an isolated 0.1.1-wheel entry-point smoke test passed. The Human confirmed that the recovered v0.1.1 workflow completed validation, PyPI publication, and GitHub Release creation.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-08-25 10:56
---
Human: Use PyPI Trusted Publishing, GitHub-generated release notes, and a manual existing-tag bootstrap for v0.1.0.
---

author: Human
created: 2026-08-25 11:10
---
Human: The manually dispatched v0.1.0 Release workflow failed in Run quality checks because MyPy reported hermes_constants as installed but untyped (import-untyped).
---

author: Human
created: 2026-08-25 11:13
---
Human: Preserve the existing v0.1.0 tag and make the first publication a new v0.1.1 release.
---

author: Human
created: 2026-08-25 11:21
---
Human: v0.1.1 validation and PyPI publishing succeeded, but GitHub Release creation failed because the artifact-only job had no .git directory for gh release create --verify-tag.
---

author: Human
created: 2026-08-25 11:28
---
Human: Confirmed the recovered v0.1.1 workflow completed successfully; validation, PyPI publication, and GitHub Release creation all worked. Requested task closure.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented tagged release automation with secure isolated build, PyPI Trusted Publishing, and generated-notes GitHub Release jobs. Added strict tag/package-version validation, manual recovery for an already-published version, release documentation, and the MyPy optional-import fix. Local checks passed actionlint, Ruff, format, clean MyPy, 27 tests at 100% coverage, lock/build/Twine validation, and installed-wheel smoke testing. Human-confirmed v0.1.1 completed validation, PyPI publication, and GitHub Release creation. No ADRs or follow-up tasks.
<!-- SECTION:FINAL_SUMMARY:END -->
