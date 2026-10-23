---
project: {TARGET}
created: {DATE}
updated: {DATE}
---

# Specs Index: {TARGET}

This index is navigational only. It does not replace PRD, Architecture, Story, Quick Task, or code review gates.

## Overview

- Owner: {Project for shared records, or subproject for feature records}
- Current focus: {current work}

## Native Records

`spec-create` owns this table at its returned `index_path`; retain its rows
instead of transcribing examples, guessing filenames or duplicating links.
Feature rows stay in their owner-local index; shared Quick Tasks stay in the
Project index. `work finish` updates existing row statuses, not missing rows.

| Kind | Record | Status |
| ---- | ------ | ------ |

## Research Memos

Research has no native creation kind. Add its entries here; PRD/Architecture
context belongs in the memo rather than duplicate native-record links.

| Research | Status | Recommendation |
|----------|--------|----------------|
| [Research {topic}](research/{YYYY-MM-DD}-{slug}.md) | draft | {summary} |

## Completed or Archived Research

| Research | Completed | Notes |
|----------|-----------|-------|
| {research link} | {DATE} | {summary} |

## Maintenance Notes

- Native creation owns new record rows; finish owns their completion status. Never replace or duplicate a native table to apply this template.
- Maintain research/non-native navigation manually. Reconcile historical missing rows explicitly when needed; native commands do not migrate them automatically.
- Link durable knowledge through notes rather than storing it only in this index.
