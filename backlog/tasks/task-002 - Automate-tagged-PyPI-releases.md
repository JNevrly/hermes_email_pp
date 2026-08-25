---
id: TASK-002
title: Automate tagged PyPI releases
status: In Progress
assignee:
  - '@opencode'
created_date: '2026-08-25 10:53'
updated_date: '2026-08-25 11:21'
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

6. Bump the unreleased package and changelog version to 0.1.1 so the first public artifact corresponds to a new immutable v0.1.1 tag.

7. Check out the verified tag in the GitHub Release job and add a documented manual recovery input that skips PyPI only after a version has already been published.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Release workflow: .github/workflows/release.yml isolates build/test, PyPI Trusted Publishing, and GitHub Release creation. It validates stable tags against pyproject.toml, uses an artifact to publish and attach the exact same files, and generates GitHub release notes.

CI fix: hermes_constants is optional but GitHub's clean environment exposes it as an installed untyped module. The import suppresses both import-not-found and import-untyped; its line-local Ruff I001 suppression keeps the MyPy-required statement-level ignore.

Release target: preserve the existing unpublished v0.1.0 tag. The first public release is 0.1.1/v0.1.1; pyproject.toml and uv.lock were bumped, the changelog records the first PyPI release, and the README no longer suggests bootstrapping v0.1.0.

Verification: actionlint 1.7.12 accepted the workflow. Ruff, format check, clean MyPy (--no-incremental), 27 Pytest tests at 100% coverage, uv lock --check, uv build, and twine metadata validation pass. An isolated Python 3.13 environment installed the 0.1.1 wheel with Hermes Agent 0.19.0 and loaded the email-pp entry point.

Remote verification remains: merge the fix, push v0.1.1, and confirm the workflow publishes to PyPI and creates the GitHub Release.

Release recovery fix: the GitHub Release job now checks out needs.build.outputs.tag before gh release create --verify-tag. workflow_dispatch also has a required skip_pypi boolean (default false); it skips only the upload step so an already-published version can complete its missing GitHub Release. README documents this narrow recovery use. actionlint accepts the updated workflow.
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
<!-- COMMENTS:END -->
