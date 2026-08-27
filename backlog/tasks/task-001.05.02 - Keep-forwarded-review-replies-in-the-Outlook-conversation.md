---
id: TASK-001.05.02
title: Keep forwarded review replies in the Outlook conversation
status: Done
assignee:
  - '@Josef'
created_date: '2026-08-27 11:10'
updated_date: '2026-08-27 11:20'
labels: []
dependencies: []
modified_files:
  - hermes_email_pp/adapter.py
  - hermes_email_pp/threading.py
  - tests/test_adapter.py
  - tests/test_hermes_email_pp.py
  - README.md
parent_task_id: TASK-001.05
priority: high
type: bug
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A forwarded email plus task prompt currently produces a private, unthreaded `Draft: Re: <original subject>` message. Outlook places it outside the original conversation. The first generated response must remain private to the authorized forwarder while participating in the wrapper email conversation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The first response to a recognized forward uses `Re: <original subject>` without a `Draft:` prefix.
- [x] #2 The first forwarded response includes RFC `In-Reply-To` and `References` headers targeting the wrapper message, preserving available ancestors.
- [x] #3 The response remains addressed only to the authorized forwarder and continues to quote only the forwarded original.
- [x] #4 Gmail, Outlook plain-text, and O365 HTML forwarded-review regressions verify the threaded headers and subject.
- [x] #5 Documentation describes the first response as a private threaded reply.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm the approved private threaded-reply behavior and current adapter context. 2. Emit the original-subject reply with RFC parent headers for the first forwarded response. 3. Update representative forward tests and documentation. 4. Run focused and project quality checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Investigation confirmed the prior workflow intentionally created an unthreaded `Draft: Re:` message. The approved replacement uses standard RFC reply threading for the forwarding wrapper; recipient isolation and prompt exclusion remain unchanged.

Implemented standard RFC reply headers for the initial forwarded response and removed the subject `Draft:` prefix. The adapter now retains `In-Reply-To` as an ancestor fallback, and both adapter and router safely unfold RFC folded Message-ID chains while rejecting other newline-containing values. Quality gate excluding the known repository plugin-scan false positive: Ruff check/format, MyPy, and 44 pytest cases at 100% coverage.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @Josef
created: 2026-08-27 11:11
---
Human: Approved the normal threaded-reply approach: remove the `Draft:` prefix and send the first response only to the authorized forwarder with standard `In-Reply-To` and `References` headers.
---

author: @Josef
created: 2026-08-27 11:13
---
Agent: Implementation and verification are complete and ready for human review. The configured statuses have no review state, so this task remains In Progress for human acceptance.
---

author: @Josef
created: 2026-08-27 11:18
---
Human: Tested the threaded forwarded-review reply, approved the result, and requested task closure and version 0.3.3.
---

author: @Josef
created: 2026-08-27 11:20
---
Agent: Closed following human acceptance and synchronized release metadata for version 0.3.3. `uv lock --check`, Ruff, package build, and version metadata tests pass. The full release test file has one existing unrelated plugin-scan failure because the workspace is classified as dangerous.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced the first forwarded-review result’s unthreaded `Draft: Re:` delivery with a private RFC-threaded `Re:` reply. The reply retains the forwarding wrapper as its parent, preserves valid ancestor Message-IDs including legal folded chains, and remains addressed only to the authorized forwarder. Updated Gmail, Outlook plain-text, and O365 HTML regressions plus documentation. Verified with Ruff check and format check, MyPy, and pytest coverage: 44 passed, 1 known unrelated plugin-scan test deselected, 100% coverage. The unfiltered suite’s plugin scan fails only because existing untracked `.release-venv` content is detected.
<!-- SECTION:FINAL_SUMMARY:END -->
