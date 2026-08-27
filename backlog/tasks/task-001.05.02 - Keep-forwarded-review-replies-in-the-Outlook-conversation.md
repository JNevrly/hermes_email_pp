---
id: TASK-001.05.02
title: Keep forwarded review replies in the Outlook conversation
status: In Progress
assignee:
  - '@Josef'
created_date: '2026-08-27 11:10'
updated_date: '2026-08-27 12:58'
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
Real Outlook testing showed that the 0.3.3 RFC-only reply remains in a separate conversation. Delivered MIME comparison proves that the response uses the inline forwarded subject, omits Outlook conversation headers, and serializes long RFC reply identifiers as invalid encoded words. The first private forwarded-review response must reproduce the forwarding wrapper conversation across Outlook, O365, and Gmail without sending to the original correspondent.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The first forwarded-review response uses the forwarding wrapper subject with one `Re:` prefix, rather than the inline forwarded subject.
- [ ] #2 Long `In-Reply-To` and `References` Message-ID values serialize as literal RFC Message-ID tokens, never RFC-2047 encoded words.
- [ ] #3 When the wrapper has valid Outlook `Thread-Topic` and `Thread-Index` headers, the response preserves the topic and emits a child index whose bytes begin with the complete parent index and add one five-byte response level.
- [ ] #4 Malformed or absent Outlook conversation headers safely retain standard RFC reply behavior without emitting invalid proprietary headers.
- [ ] #5 Gmail, Outlook plain-text, and O365 HTML forwarded-review regressions verify private delivery, standard RFC linkage, byte-level serialization, wrapper subject continuity, and Outlook conversation metadata.
- [ ] #6 Documentation describes both standard reply headers and Outlook conversation metadata for forwarded-review replies.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Preserve the forwarding wrapper subject and valid Outlook conversation metadata per inbound parent message. 2. Generate a Microsoft-compatible child `Thread-Index` and emit it with `Thread-Topic`. 3. Serialize RFC reply IDs with a safe long-line policy that prevents encoded-word corruption on Python 3.11/3.12. 4. Add byte-level synthetic Outlook/Gmail/O365 regressions, run quality checks, and request a real Outlook retest.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Investigation confirmed the prior workflow intentionally created an unthreaded `Draft: Re:` message. The approved replacement uses standard RFC reply threading for the forwarding wrapper; recipient isolation and prompt exclusion remain unchanged.

Implemented standard RFC reply headers for the initial forwarded response and removed the subject `Draft:` prefix. The adapter now retains `In-Reply-To` as an ancestor fallback, and both adapter and router safely unfold RFC folded Message-ID chains while rejecting other newline-containing values. Quality gate excluding the known repository plugin-scan false positive: Ruff check/format, MyPy, and 44 pytest cases at 100% coverage.

Compared private `temp/split_response.eml` and `temp/kept_in_thread.eml`. The split response lacked `Thread-Topic`/`Thread-Index`, used the inline subject, and had RFC reply IDs serialized as encoded words. Implemented wrapper-subject replies, parent-ID-scoped Outlook metadata, compatible child-index generation, and a 998-character SMTP policy with a 900-character reference chain cap. Validation passed: Ruff check/format, MyPy, pytest (47 passed, 1 known plugin-scan test deselected, 100% coverage), and a direct Python 3.11 serialization check. Awaiting a real Outlook retest before release/version bump.

Prepared testing release 0.3.4: synchronized pyproject, manifest, package version, changelog, and uv.lock. Built wheel and source distribution. Release validation passed except for the known repository plugin-scan false positive; 25 remaining release tests pass.
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

author: @Josef
created: 2026-08-27 12:44
---
Human: Tested 0.3.3 in Outlook. The `Draft:` prefix is gone, but the response remains in a separate conversation. Supplied raw split and successful in-thread .eml samples for comparison and approved implementing the proposed comprehensive fix.
---

author: @Josef
created: 2026-08-27 12:51
---
Agent: The Outlook-compatible reply implementation is ready for a real mailbox retest. Please send another forwarded-review request from Outlook and confirm whether the first Email++ response appears in the same conversation; export its raw .eml only if it still splits.
---

author: @Josef
created: 2026-08-27 12:58
---
Human: Requested version 0.3.4 so the Outlook conversation fix can be used on the running instance.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced the first forwarded-review result’s unthreaded `Draft: Re:` delivery with a private RFC-threaded `Re:` reply. The reply retains the forwarding wrapper as its parent, preserves valid ancestor Message-IDs including legal folded chains, and remains addressed only to the authorized forwarder. Updated Gmail, Outlook plain-text, and O365 HTML regressions plus documentation. Verified with Ruff check and format check, MyPy, and pytest coverage: 44 passed, 1 known unrelated plugin-scan test deselected, 100% coverage. The unfiltered suite’s plugin scan fails only because existing untracked `.release-venv` content is detected.
<!-- SECTION:FINAL_SUMMARY:END -->
