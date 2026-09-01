---
id: TASK-017
title: Tighten automated-sender matching
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-29 00:00'
updated_date: '2026-09-01 12:37'
labels:
  - email
  - security
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
modified_files:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
priority: low
type: bug
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`_permitted` rejects a sender when any of `("noreply", "no-reply", "mailer-daemon", "postmaster", "bounce")` appears anywhere in the address via `any(x in sender ...)`. Because this is a plain substring test over the whole address, legitimate allowlisted addresses such as `bounceback@example.com`, or a local part containing `no-reply-team`, are silently rejected. The impact is low since the allowlist already gates senders, but the match is looser than intended. Match the automated local-parts more precisely.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Automated-sender detection matches the local part with word boundaries or by exact local-part comparison, not arbitrary substrings of the full address
- [x] #2 Known automated senders (noreply, no-reply, mailer-daemon, postmaster, bounce daemons) are still rejected
- [x] #3 Legitimate addresses that merely contain those substrings are accepted (subject to the allowlist)
- [x] #4 Tests cover both the rejected automated cases and the previously false-positive addresses
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extract the sender local part before `@` and reject it only when it exactly matches an automated marker.
2. Preserve allowlist and authentication behavior while adding parameterized tests for automated and look-alike local parts.
3. Run the focused tests, then the project lint, type, formatting, and full test checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Discovered during the 2026-08-29 code review. Marker tuple defined at adapter.py:55 and used at adapter.py:960 (`any(x in sender for x in _AUTOMATED)`).

Confirmed _permitted receives the normalized address returned by _address() at adapter.py:830; exact local-part matching is sufficient to preserve documented automated addresses while accepting bounceback and no-reply-team.

Implemented exact local-part matching and added 8 focused regression cases: all configured automated local parts are rejected, while bounceback, no-reply-team, and a domain containing bounce are allowed. Focused pytest and Ruff lint passed; formatter applied its required layout change before full verification.

Verification: 8 focused automated-sender cases passed. With Hermes Agent supplied as an editable local dependency, the full suite ran 68 tests successfully. Ruff lint/format and mypy passed. The standard tox test environment remains unable to collect because its uv sync removes the undeclared Hermes Agent dependency (gateway); the dependency-supplied full run then misses the pre-existing 100% coverage gate at adapter.py:511 and 518-520 (99.66%).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced full-address substring matching with exact sender local-part matching and added automated-sender regression tests. Verified all 8 focused cases, plus 68 full-suite tests with the local Hermes Agent dependency; lint, format, and mypy pass. The existing coverage gate remains at 99.66% for unrelated IMAP error-path lines.
<!-- SECTION:FINAL_SUMMARY:END -->
