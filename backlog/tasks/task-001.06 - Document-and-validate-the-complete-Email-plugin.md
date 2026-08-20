---
id: TASK-001.06
title: Document and validate the complete Email++ plugin
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-18 12:54'
updated_date: '2026-08-20 13:22'
labels: []
dependencies:
  - TASK-001.05
references:
  - README.md
  - 'https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins'
parent_task_id: TASK-001
priority: high
type: task
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Finish the feature with operator documentation and end-to-end release validation after all implementation tasks are complete. Validate the built artifacts and prove that a clean Hermes Agent installation discovers and registers email_pp without disturbing the built-in email platform.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README documents installation into the Hermes environment, plugin enablement, all EMAIL_PP_* settings, quote modes, and disabling the built-in adapter for a shared mailbox
- [x] #2 README documents ordinary replies, separate forwarded review drafts, draft revision behavior, supported Gmail and Outlook formats, parsing limitations, and fail-closed behavior
- [x] #3 README documents credential storage, allowlisting, sender authentication, attachment handling, local context persistence, and mailbox security recommendations
- [x] #4 Distribution artifacts build successfully and their metadata, package contents, and entry point are validated
- [x] #5 In a clean environment with a recent supported Hermes Agent release, plugin discovery loads email-pp and the platform registry contains both email and email_pp as distinct registrations
- [x] #6 The final full test suite covers plugin registration, thread isolation, restart persistence, transport security, MIME structure, quote modes, forward parsing, prompt exclusion, draft delivery, and draft revision continuity
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Ruff check and format check pass
- [x] #2 MyPy passes for the package
- [x] #3 Pytest passes with the configured coverage threshold
- [x] #4 Package build and artifact validation pass after the implementation checks
- [x] #5 Hermes registration smoke test passes as the final verification step
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Document installation, EMAIL_PP_* configuration, reply and forwarded-draft workflows, limitations, and security guidance in README.md.
2. Restrict source-distribution contents to publishable files and expose the pip entry point as the plugin module, which Hermes can load and invoke through its register() attribute.
3. Depend on a published Hermes release range validated by the clean-environment smoke test rather than an unavailable source commit.
4. Run Ruff, MyPy, Pytest with coverage, build artifacts, validate wheel metadata/content/entry point, and smoke-test registry discovery in a clean Hermes environment.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
README now documents targeted Hermes installation and entry-point enablement, all EMAIL_PP_* settings, shared-mailbox separation, ordinary replies, the Gmail/Outlook review-draft workflow, fail-closed parsing, local context retention, attachments, and security controls. Runtime behavior and its coverage already exist in the implementation tests; release checks remain.

Release validation results: Ruff check and format check pass; MyPy passes; 27 Pytest tests pass with 100% coverage. `uv build --out-dir dist --clear` builds wheel and sdist. Wheel metadata, publishable contents, and `[hermes_agent.plugins] email-pp = hermes_email_pp.plugin` validate. The original `:register` entry-point target failed real Hermes discovery because PluginManager expects a loaded module with a register() attribute; the entry point was corrected to the module, then a clean venv with cached Hermes Agent 0.19.0 successfully registered distinct `email` and `email_pp` entries.

Blocked: the required Hermes Agent Git revision e02d1e41fc6104187e20af9eac8b2820566e3508 cannot be fetched in this environment. `uv pip install` and `uv sync` both time out after attempting that Git update; the commit is absent from uv's local Git object store, and no matching 0.20.4 PyPI release exists. Do not mark acceptance criterion 5 or Definition of Done item 5 until the pinned-revision smoke test can run.

Resolved the Git-fetch blocker per the Human clarification: the package now depends on published `hermes-agent>=0.19,<0.20`, and `uv sync --group dev` installs Hermes Agent 0.19.0 successfully. Hermes 0.19.0 requires BasePlatformAdapter.get_chat_info(), so EmailPPAdapter now implements address-based chat metadata and has coverage. A newly created clean virtual environment installed the built wheel with dependencies normally and verified the `email-pp` entry point plus distinct `email` and `email_pp` registry entries.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-08-20 13:18
---
The particular Hermes commit pin should be disregarded; validation against any recent Hermes release is acceptable.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Documented Email++ installation, configuration, workflows, limitations, and security guidance. Corrected the pip entry point to expose the plugin module, limited source-distribution contents, and replaced the unavailable Git snapshot with published Hermes Agent 0.19.x support. Added the Hermes-required get_chat_info() implementation. Verified Ruff, formatting, MyPy, 27 Pytest tests at 100% coverage, artifact metadata/content, and clean-wheel discovery/registration against Hermes Agent 0.19.0.
<!-- SECTION:FINAL_SUMMARY:END -->
