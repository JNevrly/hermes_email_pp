---
id: TASK-004
title: Expose all Email++ settings in the Channels card
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-26 07:32'
updated_date: '2026-08-26 10:06'
labels:
  - dashboard
  - configuration
  - hermes-core
dependencies: []
references:
  - /tmp/opencode/hermes-agent-v0.20.5/gateway/platform_registry.py
  - /tmp/opencode/hermes-agent-v0.20.5/hermes_cli/web_server.py
  - /tmp/opencode/hermes-agent-v0.20.5/web/src/pages/ChannelsPage.tsx
  - hermes_email_pp/config.py
  - hermes_email_pp/plugin.py
priority: high
type: feature
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Expose all 13 Email++ settings in the existing, unmodified Hermes Channels card.

Email++ uses only vanilla Hermes 0.20.5 interfaces: it registers all field metadata in Hermes' existing OPTIONAL_ENV_VARS registry when the plugin loads. The stock card renders text/password controls; descriptions document defaults and accepted values, while blank optional fields retain Email++ runtime defaults.

Hermes hides *_ALLOW_ALL_USERS optional fields from setup cards. Email++ therefore declares EMAIL_PP_ALLOW_ALL_USERS as a required card input so it remains visible; users enter false to retain the secure runtime default. The four mailbox credentials and this explicit safety input are required in the card; the other eight settings remain optional. No Hermes core or frontend changes are required.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Email++ uses vanilla Hermes plugin interfaces only; it does not require a new Hermes core descriptor API or frontend build.
- [x] #2 The stock Channels card discovers all 13 Email++ environment settings after plugin loading.
- [x] #3 The four mailbox credentials and explicit EMAIL_PP_ALLOW_ALL_USERS input are required in the card; entering false retains the secure default and the other eight settings remain optional with runtime defaults.
- [x] #4 Field metadata provides descriptive labels, passwords, defaults, quote-mode values, and an EMAIL_PP_ALLOW_ALL_USERS warning within stock text/password controls.
- [x] #5 Email++ remains loadable on Hermes 0.20.5 and does not require a custom Hermes container image.
- [x] #6 Plugin tests cover vanilla metadata registration, Channels discovery, configuration preservation, manifest metadata, and version synchronization.
- [x] #7 README documents the stock Channels configuration flow and accepted text values for non-textual settings.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove the unpublished PlatformField dependency and rich-core contract from Email++.
2. Populate vanilla Hermes OPTIONAL_ENV_VARS with all Email++ field metadata at plugin registration.
3. Verify the stock Channels catalog discovers all 13 fields with the four mailbox credentials plus explicit Allow all users input required.
4. Update documentation and regression coverage for text/password controls, runtime defaults, and version 0.2.2.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The initial PlatformField approach was removed because it required unpublished Hermes core and frontend changes. Email++ now mutates the existing hermes_cli.config.OPTIONAL_ENV_VARS mapping when register() runs, so vanilla Channels discovery merges all Email++ settings by its EMAIL_PP_ prefix.

Vanilla Hermes hides *_ALLOW_ALL_USERS optional variables from setup cards. EMAIL_PP_ALLOW_ALL_USERS is consequently declared as a required card input; users must enter false for the secure runtime default. The remaining eight non-credential settings remain optional and blank values use adapter defaults.

Verified: .venv/bin/ruff check ., .venv/bin/mypy hermes_email_pp, and .venv/bin/pytest (38 passed). uv build produced hermes_email_pp-0.2.2.tar.gz and hermes_email_pp-0.2.2-py3-none-any.whl under /tmp/opencode/email-pp-0.2.2. The referenced Hermes checkout is clean; no core or frontend changes remain.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @human
created: 2026-08-26 07:32
---
Human: Requested that all Email++ settings be configurable in the existing Channels card, selected typed controls, and requested continued Hermes 0.20.5 compatibility.
---

author: @human
created: 2026-08-26 08:55
---
Human: Reviewed the Task-004 implementation and confirmed it seems OK; requested the 0.2.1 version bump.
---

author: @human
created: 2026-08-26 09:26
---
Human: After removing the previous Email++ plugin, installing v0.2.1, enabling it, restarting the Hermes container, and opening Channels > Configure, only the original four fields appeared.
---

author: @human
created: 2026-08-26 09:58
---
Human: Requested a solution compatible with current vanilla Hermes rather than an unpublished core API, and approved using the existing environment metadata path.
---

author: @opencode
created: 2026-08-26 10:06
---
Agent: Vanilla Hermes filters optional *_ALLOW_ALL_USERS settings from Channels. To expose this security-sensitive setting without core changes, Email++ makes it a required card input and documents that false preserves the secure runtime default.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reworked Email++ 0.2.2 to use vanilla Hermes Channels discovery only. The plugin registers all EMAIL_PP metadata in OPTIONAL_ENV_VARS, leaving no Hermes core or frontend changes. The stock card exposes all 13 text/password fields; four mailbox credentials plus Allow all users are required, and false keeps the secure allow-all default. Verified with Ruff, mypy, 38 pytest tests, and a source/wheel build. No ADRs or follow-up tasks.
<!-- SECTION:FINAL_SUMMARY:END -->
