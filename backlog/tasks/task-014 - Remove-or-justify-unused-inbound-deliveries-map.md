---
id: TASK-014
title: Remove or justify unused inbound-deliveries map
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-29 00:00'
updated_date: '2026-09-01 06:32'
labels:
  - email
  - cleanup
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
priority: low
type: chore
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`EmailPPAdapter._inbound_deliveries` has an entry inserted in `_dispatch` and removed in `on_processing_complete`, but the stored `_InboundMail` value is never read: `on_processing_complete` recovers the delivery from `event.raw_message`. The dict is dead state that costs memory and implies a correlation guarantee it does not actually provide. Either remove it or make it the authoritative source of the delivery so its presence is meaningful.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `_inbound_deliveries` is either removed entirely or its stored value is actually consumed
- [x] #2 Deletion/acknowledgement behavior is unchanged for success, rejection, failure, and cancellation outcomes
- [x] #3 Existing tests still pass and any test referencing the map is updated to match the chosen approach
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove `_inbound_deliveries` initialization, dispatch insertion, and completion pop; preserve `MessageEvent.raw_message` as the delivery identity.
2. Remove map-specific test setup/assertions and assert dispatch carries the exact delivery in `raw_message`.
3. Cover success, failure, cancellation, and rejection acknowledgement behavior.
4. Run focused tests, formatting, linting, type checking, and the full coverage suite.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Removed the unused inbound-deliveries map from adapter initialization, dispatch, and completion. Delivery identity remains on MessageEvent.raw_message; tests assert the attribute is absent, dispatched events preserve the delivery, and cancellation releases it for retry. Validation passed: uv run pytest --cov=hermes_email_pp tests/ passed 58 tests at 100% coverage; Ruff lint and format checks and MyPy passed. The prior plugin_guard blocker was resolved by TASK-016.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-08-31 12:12
---
Human: Approved removing the dead map rather than making it authoritative.
---

author: @opencode
created: 2026-09-01 06:32
---
Human: Requested TASK-016 and TASK-014 be closed once all tests pass.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed redundant inbound-deliveries state and updated delivery-completion tests for raw-message identity and cancellation retry behavior. Verified by the 58-test full suite at 100% coverage, Ruff, and MyPy.
<!-- SECTION:FINAL_SUMMARY:END -->
