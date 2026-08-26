---
id: TASK-004
title: Expose all Email++ settings in the Channels card
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-26 07:32'
updated_date: '2026-08-26 08:55'
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
Provide a complete, typed Email++ configuration experience in the existing Hermes Dashboard Channels card.

Hermes core currently exposes only a platform plugin's required environment variables. It must gain a generic, backward-compatible platform-field descriptor contract so third-party platforms can declare optional settings, labels, descriptions, passwords, defaults, input types, and select options. Email++ will then declare all 13 of its settings through that contract.

Scope includes coordinated Hermes core and Email++ changes. The Email++ plugin must continue to load on Hermes 0.20.5: when the richer core API is unavailable, it retains the existing four required-field card.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Hermes exposes an additive platform registration schema for required and optional Channel settings with label, description, password, type, default, select options, and advanced metadata.
- [x] #2 The Channels API and UI render plugin-declared text, password, number, boolean, and select controls while existing required_env-only plugins retain current behavior.
- [x] #3 Channels validates typed plugin settings atomically before persistence, preserves untouched values, and supports explicitly clearing a field to restore its effective default.
- [x] #4 Non-secret saved settings round-trip into their controls; secrets remain write-only and reveal only whether a value is set.
- [x] #5 Email++ exposes its four required and nine optional settings in its Channels card with the documented defaults, correct control types, descriptions, and quote-mode choices.
- [x] #6 Email++ provides clear warnings for EMAIL_PP_ALLOW_ALL_USERS and preserves the documented sender-authentication default.
- [x] #7 Email++ remains loadable on Hermes 0.20.5 and falls back to its current four required fields when rich field descriptors are unsupported.
- [x] #8 Core and plugin tests cover descriptor compatibility, typed rendering, validation, clearing, profile isolation, metadata synchronization, and Email++ Channels discovery.
- [x] #9 README documentation explains the complete Email++ Channels configuration flow.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add an additive PlatformField descriptor to Hermes platform registration while retaining required_env behavior.
2. Use descriptors in Channels catalog/API for typed metadata, value serialization, validation-before-write, and clearing.
3. Render typed descriptor controls in Channels and preserve existing required_env-only behavior.
4. Register all Email++ fields conditionally, document the dashboard flow, and add core/plugin regression coverage.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented the additive PlatformField contract in the referenced Hermes 0.20.5 checkout. Channel descriptors remain environment-backed to preserve the existing Channels persistence model; validation now completes before any field write, and explicit clear_env restores descriptor defaults.

Email++ declares 13 fields only when PlatformField is present. On unmodified Hermes 0.20.5 it omits the unknown keyword and retains the four required credential fields.

Verified: Email++ ruff, mypy, and 39 pytest tests; Hermes descriptor plus profile-scoping tests (12 passed); web typecheck and production build. npm lint exited successfully with 26 pre-existing warnings outside this change.
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
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added typed Channels descriptors and controls in Hermes, conditional Email++ registration for all 13 settings, fallback support for Hermes 0.20.5, documentation, and regression coverage. Verified with the Email++ suite (39 passed), Hermes descriptor/profile suites (12 passed), web typecheck, and production build. No ADRs or follow-up tasks.
<!-- SECTION:FINAL_SUMMARY:END -->
