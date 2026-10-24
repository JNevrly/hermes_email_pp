---
id: TASK-022
title: Recover the Python 3.14 compatibility release metadata
status: In Progress
assignee:
  - '@opencode'
created_date: '2026-10-24 17:40'
updated_date: '2026-10-24 17:42'
labels:
  - awaiting-human-review
dependencies: []
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Recover the intended 0.5.1 Python compatibility release after GitHub run 40116792708 failed before exposing any step details. Synchronize versions to 0.5.1. Keep release validation reproducible with the existing Hermes 0.20.5 test host by selecting Python 3.13 explicitly and preserving the manually installed host during quality checks. The immediate no-step runner failure remains unexplained; do not attribute it to these confirmed release blockers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Package version, plugin manifest, module version, editable lock entry, and changelog agree on 0.5.1.
- [x] #2 Lock consistency, existing plugin contract tests, lint, and distribution build pass.
- [x] #3 Record observed GitHub failure evidence, distinguish confirmed blockers from unknown causes, and provide the required tag recovery guidance.
- [x] #4 Release workflow explicitly selects Python 3.13 for its existing Hermes 0.20.5 host, and quality commands preserve that installed host.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect GitHub run jobs and annotations and compare the tag with metadata. 2. Synchronize all version sources and add the compatibility changelog entry. 3. Run locked sync, existing contract tests, lint, and build; record evidence and explain that the existing tag points at the old commit.

4. Configure setup-uv python-version 3.13 and use uv run --no-sync for checks, because the host excludes 3.14 and exact uv syncing demonstrably removes it. Validate workflow with actionlint and execute the updated check commands.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Public GitHub API evidence: run 40116792708, build job 120939616450 has an empty steps array; check annotations contain only exit code 1 and a notice about ubuntu-latest migrating to Ubuntu 26. No root cause for the early runner failure is exposed. Local tag v0.5.1 and remote run point to b5bcf3264543617bf31fd1175a12343888e2691e, whose pyproject declares 0.5.0. The workflow explicitly rejects this mismatch. gh is installed but unauthenticated, so inspection used public API endpoints. No remote mutations performed.

Additional confirmed release constraints: checked-in workflow installs Hermes 0.20.5, which declares >=3.11,<3.14; expanding plugin range allows uv to select 3.14 on newer runners. Also, the previous session and this session observed exact uv sync removing the manually installed host. Keep CI on the existing 3.13 host baseline and use --no-sync in quality checks. This does not claim Hermes 0.22 integration.

Implemented all five version sources for 0.5.1 (pyproject, manifest, module, changelog, regenerated lock). Release workflow now explicitly requests Python 3.13 through setup-uv and runs quality commands with --no-sync to preserve its installed Hermes 0.20.5 host.

Verification: uv lock --check and uv sync --group dev --locked passed. Installed the existing editable Hermes test host after sync. Ran the exact updated workflow quality commands: Ruff passed, all 10 files formatted, MyPy passed on 7 sources, and all 80 tests passed with 100% coverage on Python 3.13.15. /tmp/opencode/actionlint .github/workflows/release.yml passed. uv build --out-dir /tmp/opencode/email-pp-0.5.1 produced hermes_email_pp-0.5.1.tar.gz and hermes_email_pp-0.5.1-py3-none-any.whl. git diff --check passed. Old 0.5.0 version search in TOML/YAML/Python sources found no matches.

Recovery guidance: commit the local fixes, then ensure the release tag points at that corrected commit before pushing/triggering a release. Existing v0.5.1 still points at b5bcf32; rerunning that tag or dispatching it would use the old metadata/workflow. Replacing the failed unpublished tag requires explicit human action/authorization. No commits, tags, pushes, CI reruns, or publications were performed by the agent.

Limitation: the immediate cause of the initial empty-step GitHub failure is not available in public API output. If it recurs with corrected metadata, inspect runner setup logs or GitHub Actions service status. Full Hermes 0.22 integration remains unverified. Ready for review; retained In Progress with awaiting-human-review label because no Review status is configured. No ADRs or additional follow-up tasks created.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-10-24 17:40
---
Human: Committed, tagged, and pushed the Python compatibility change; CI failed at the beginning with only Process completed with exit code 1 and no logs.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Prepared a consistent 0.5.1 release and hardened the existing release-host validation with Python 3.13 and no-sync quality commands. Verified lock/sync, lint/format/types, 80 tests at 100% coverage, actionlint, and wheel/sdist builds. Confirmed the old v0.5.1 tag has 0.5.0 metadata; the separate no-step runner failure remains unexplained by GitHub output. Corrected commit must be tagged before retrying publication. Awaiting human review.
<!-- SECTION:FINAL_SUMMARY:END -->
