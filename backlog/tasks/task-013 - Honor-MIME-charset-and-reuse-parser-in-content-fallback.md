---
id: TASK-013
title: Honor MIME charset and reuse parser in content fallback
status: Done
assignee:
  - '@opencode'
created_date: '2026-08-29 00:00'
updated_date: '2026-08-31 11:17'
labels:
  - email
  - mime
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - hermes_email_pp/forwarding.py
  - tests/test_adapter.py
modified_files:
  - hermes_email_pp/adapter.py
  - tests/test_adapter.py
priority: medium
type: bug
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`EmailPPAdapter._content` extracts a body for messages without a text/plain part, but its text/html branch decodes the payload as UTF-8 unconditionally and strips markup with a naive `re.sub(r"<[^>]+>", "")`. This is inconsistent with the text/plain branch in the same method and with `_text_alternatives`, both of which respect `part.get_content_charset()`, and it bypasses the project's own `html_to_text` parser. As a result an HTML-only message in a non-UTF-8 charset is garbled, entities are left unescaped, and malformed markup can leak into the extracted text. Decode with the declared charset and route the HTML fallback through `html_to_text`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The text/html fallback decodes using the part's declared charset with a safe UTF-8 default
- [x] #2 HTML is converted to text via the shared `html_to_text` parser instead of naive regex tag stripping
- [x] #3 Behavior matches `_text_alternatives` for the same HTML-only input
- [x] #4 Tests cover a non-UTF-8 HTML-only message and confirm correct decoding and entity handling
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Decode the HTML-only fallback with `part.get_content_charset() or "utf-8"` and `errors="replace"`.
2. Convert that decoded HTML with the existing `html_to_text` parser.
3. Add an ISO-8859-1 HTML-only regression test that asserts parser parity and entity handling.
4. Run focused tests plus the project lint, formatting, type, and coverage checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Discovered during the 2026-08-29 code review. The text/plain branch already uses get_content_charset(), and _text_alternatives already routes HTML through html_to_text, so this change aligns the fallback with existing behavior.

Implemented the HTML-only fallback with the same declared-charset decode and html_to_text conversion used by _text_alternatives. Added ISO-8859-1 HTML-only coverage for accented text, entity decoding, and exact parser parity. Verified: focused regression test (1 passed); Ruff lint and format checks; mypy (no issues); and the coverage suite excluding test_repository_root_has_a_safe_hermes_plugin_scan (57 passed, 1 deselected, 100% coverage). The unfiltered suite has the existing unrelated plugin-guard verdict failure: dangerous rather than safe.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @opencode
created: 2026-08-31 10:11
---
Agent: Implementation and verification are ready for human review. The only unfiltered-suite failure is the pre-existing plugin-guard safety-scan verdict, unrelated to this task.
---

author: @opencode
created: 2026-08-31 10:12
---
Agent: Correction to the finalization record: the known unfiltered test failure is the plugin-guard scan reporting dangerous rather than safe; it is unrelated to TASK-013.
---

author: @human
created: 2026-08-31 11:17
---
Human: Reviewed the implementation and requested that TASK-013 be closed.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aligned the HTML-only content fallback with the shared MIME parser: it now honors each part's declared charset and converts HTML through html_to_text. Added ISO-8859-1 parity coverage for accented text and HTML entities. Focused regression, Ruff lint/format, mypy, and the coverage suite excluding the known unrelated plugin-guard scan all pass. No ADRs or follow-up tasks are needed.
<!-- SECTION:FINAL_SUMMARY:END -->
