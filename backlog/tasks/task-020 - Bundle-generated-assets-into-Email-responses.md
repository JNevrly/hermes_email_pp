---
id: TASK-020
title: Bundle generated assets into Email++ responses
status: Done
assignee:
  - '@opencode'
created_date: '2026-09-04 09:53'
updated_date: '2026-09-04 11:22'
labels: []
dependencies: []
references:
  - hermes_email_pp/adapter.py
  - hermes_email_pp/plugin.py
  - hermes_email_pp/rendering.py
  - hermes_email_pp/config.py
  - README.md
priority: high
type: feature
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deliver agent-generated assets as MIME attachments on the same Email++ response that contains the final body, without modifying Hermes Agent upstream. For in-process Hermes execution, Email++ must use the existing polymorphic response-extraction hooks and a bounded, versioned private extraction envelope to carry validated explicit MEDIA attachment metadata into the final send operation. Bare local paths and local HTTP links remain valid informational references and must not be promoted automatically. The feature must fail visibly rather than silently sending a body without requested assets, preserve secure path validation and SMTP threading, and remain compatible with the supported Hermes Agent 0.20.5 pipeline.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Hermes Agent upstream files and APIs are not modified; the feature is implemented entirely by the Email++ plugin against the existing Hermes Agent 0.20.5 framework.
- [x] #2 The Email++ platform hint instructs the agent to use MEDIA:/absolute/path when a user asks to receive an asset and clarifies that a path or link must not substitute for the requested attachment.
- [x] #3 The platform hint permits local paths and local HTTP URLs as informational references, including alongside a separately attached asset.
- [x] #4 For an in-process final response containing body text and one or more valid explicit MEDIA directives, the recipient receives one SMTP message containing the final plain/HTML body and every requested MIME attachment.
- [x] #5 An explicit attachment-only response still produces one valid MIME email containing all requested attachments.
- [x] #6 Bare local paths, relative paths, ordinary HTTP or localhost links, and remote image references remain visible references and are not implicitly downloaded or attached by Email++.
- [x] #7 Explicit attachments preserve order, deduplicate repeated paths, use safe filenames and inferred MIME types, and fall back to application/octet-stream when no type is known.
- [x] #8 Attachment paths are validated during extraction and revalidated immediately before reading; unsafe, missing, non-regular, unreadable, or changed files are never attached.
- [x] #9 If any requested attachment fails validation or preflight, Email++ sends one threaded failure notice with no partial attachments and treats an SMTP-accepted notice as a handled response.
- [x] #10 Outbound attachment limits are configurable and default to at most 10 files and 15 MiB of total raw attachment bytes before MIME encoding.
- [x] #11 Attachment-bearing responses never fall back silently to body-only delivery, and retry behavior avoids automatic resend after ambiguous SMTP DATA acceptance.
- [x] #12 Email++ declares that sent messages cannot be edited so normal in-process final delivery is non-streaming and MIME is constructed only after the complete response is available.
- [x] #13 Processed inbound mail is acknowledged or deleted only after SMTP accepts either the complete MIME response or the explicit attachment-failure notice.
- [x] #14 Concurrent Email++ conversations cannot exchange, overwrite, or consume each others attachment metadata.
- [x] #15 Documentation covers explicit MEDIA attachment intent, informational local references, limits, non-streaming operation, failure behavior, and the Hermes 0.20.5 extraction-order compatibility constraint.
- [x] #16 Automated tests cover envelope parsing and bounds, one and multiple attachments, attachment-only responses, preserved local references, validation failures, configured limits, MIME structure, concurrency, retries, processing completion, platform registration, and the supported Hermes extraction contract.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Override Email++ extraction hooks so only explicit MEDIA directives become a bounded response envelope while bare paths and remote image references remain body text. 2. Decode and revalidate the envelope in the final send path, preflight all attachments, and construct one multipart/mixed SMTP message or one threaded failure notice. 3. Add configurable outbound limits, explicit attachment guidance, safe rendering of image links, and non-editable-email capability. 4. Add focused mocked transport and Hermes-contract tests for success, failure, concurrency, and processing completion. 5. Run formatting, linting, typing, and full coverage validation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented the plugin-only v1 extraction envelope: Email++ consumes explicit MEDIA directives through its adapter override, returns no Hermes media calls, decodes the response-local marker in send(), revalidates and snapshots attachments, then sends one multipart/mixed email. Bare paths and image URLs remain body references. Invalid or oversized attachment sets send one threaded failure notice rather than a partial response. Added configurable 10-file and 15 MiB defaults. Validation passed: .venv/bin/ruff check .; .venv/bin/ruff format --check .; .venv/bin/mypy hermes_email_pp; .venv/bin/pytest --cov=hermes_email_pp tests/ (80 passed, 100% coverage).
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Human
created: 2026-09-04 09:54
---
The Hermes Agent upstream is considered unchangeable. Use the plugin-only extraction-envelope approach for in-process execution. Package the final body and all requested assets into one MIME email. Only explicit MEDIA directives request attachments; local paths and localhost URLs may remain informational references. On any attachment preflight failure, send a threaded failure notice with no partial attachments. Default limits are 10 files and 15 MiB total raw attachment data.
---

author: @opencode
created: 2026-09-04 11:22
---
Agent: Implementation and validation are complete; ready for human review. The only non-task worktree item is the pre-existing untracked code_review_report.html, which was not modified.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented plugin-only, in-process attachment bundling for Email++. Explicit MEDIA paths are carried in a bounded private envelope through Hermes existing extraction/send seam and are emitted as one multipart/mixed response with the final plain and HTML body. Informational local paths and HTTP/localhost references remain visible, outbound size/count limits are configurable, and invalid attachment sets produce a threaded failure notice without partial files. Added guidance, settings metadata, documentation, renderer support for image links, and mocked coverage for envelope integrity, MIME, failures, concurrency, retries, processing completion, and Hermes compatibility. Verified with Ruff, MyPy, and 80 pytest cases at 100% package coverage. No ADRs or follow-up tasks created.
<!-- SECTION:FINAL_SUMMARY:END -->
