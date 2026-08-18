---
id: TASK-001.02
title: Add per-thread routing and durable email context
status: To Do
assignee: []
created_date: '2026-08-18 12:53'
labels: []
dependencies:
  - TASK-001.01
references:
  - >-
    https://github.com/NousResearch/hermes-agent/blob/e02d1e41fc6104187e20af9eac8b2820566e3508/gateway/session.py
  - 'https://github.com/NousResearch/hermes-agent/pull/63659'
parent_task_id: TASK-001
priority: high
type: task
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Give Email++ deterministic, recipient-scoped Hermes sessions for RFC email threads and durable routing context across gateway restarts. Preserve the sender address as chat_id, supply a privacy-safe canonical thread_id, and retain the minimum context required to route later replies and draft revisions without cross-thread or cross-recipient leakage.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Two unrelated messages from the same sender resolve to different Hermes session sources
- [ ] #2 Messages connected through References or In-Reply-To resolve to the same canonical thread, including when a known Hermes-generated Message-ID is referenced
- [ ] #3 Two senders with identical subjects or reference shapes cannot share session or delivery context
- [ ] #4 Raw Message-IDs and sender addresses are not embedded in the public thread token beyond the separately required chat_id
- [ ] #5 Thread, Message-ID alias, quote-source, and draft context needed after restart are stored under the active Hermes profile with restrictive permissions and bounded retention
- [ ] #6 Missing or malformed threading headers fail toward isolation rather than merging unrelated conversations
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Ruff check and format check pass
- [ ] #2 MyPy passes for the package
- [ ] #3 Pytest passes with the configured coverage threshold
<!-- DOD:END -->
