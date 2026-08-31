---
id: TASK-011
title: Bound in-memory route and reply-context maps
status: Done
assignee:
  - '@Josef'
created_date: '2026-08-29 00:00'
updated_date: '2026-08-31 08:58'
labels:
  - email
  - reliability
  - memory
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
priority: medium
type: bug
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`EmailPPAdapter._routes` and `EmailPPAdapter._outlook_reply_context` gain an entry for every inbound message carrying a Message-ID and every outbound reply, but nothing ever removes entries. Unlike `EmailThreadRouter`, which prunes its persisted state by retention and max-thread count, these two process-lifetime dictionaries grow without limit, producing a slow memory leak proportional to total messages handled by a long-running gateway. Bound their footprint so it tracks active threads rather than lifetime volume.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `_routes` and `_outlook_reply_context` have an enforced upper bound (max size and/or TTL) so they cannot grow without limit
- [x] #2 Eviction does not break send routing or Outlook reply-context lookup for still-active threads
- [x] #3 The bound is consistent with the router's existing retention/max-thread policy
- [x] #4 Regression tests cover eviction under sustained message volume and confirm active routes still resolve
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the router retention/max-thread policy and adapter lookup paths.
2. Bound both adapter maps using the same active-thread maximum while preserving recent entries.
3. Add sustained-volume regression coverage for eviction and active reply routing.
4. Run focused and project checks, then document results for review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Discovered during the 2026-08-29 code review. Entries are added at adapter.py:775-776 (inbound), :952 and :1104 (outbound) and read at :1089/:1102; there is no removal path. The on-disk `EmailThreadRouter` already prunes, so aligning these in-memory maps with the same retention is the natural fix.

Investigation: EmailThreadRouter retains at most 500 active threads by default. Adapter maps are keyed by recipient and message ID; a shared 500-entry LRU bound, refreshed on reply lookup, constrains lifetime growth while retaining recent active reply routes and Outlook metadata.

Validation: uv run pytest tests/test_adapter.py -q passed (29 tests). uv run ruff check . and uv run ruff format --check . passed; uv run mypy hermes_email_pp passed. Full pytest with coverage reached 100% (55 passed); its sole unrelated failure is plugin_guard scanning .release-venv, tracked by TASK-016.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @Josef
created: 2026-08-31 08:58
---
Agent: Implementation and acceptance criteria are verified; ready for human review. The unrelated full-suite plugin_guard failure is tracked by TASK-016.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented bounded LRU caches for reply routes and Outlook context, with a capacity shared with EmailThreadRouter's 500-thread policy. Cache hits refresh recency, and all inbound/outbound route writes use the common eviction path. Added sustained-volume coverage for eviction, active reply routing, and Outlook Thread-Topic preservation.

Verification: focused adapter tests, Ruff lint/format, and mypy pass. Full coverage run reached 100%, with one unrelated plugin_guard .release-venv failure tracked by TASK-016.

Known limitation/follow-up: full suite remains blocked only by TASK-016; no ADRs created.
<!-- SECTION:FINAL_SUMMARY:END -->
