---
status: draft
created: {DATE}
updated: {DATE}
result: create
scope: project-procedure
target: {skill-name}
target_ref: skill://{skill-name}
target_sha256: empty
proposer_mode: same-agent
proposer_ref: agent://{agent-id}
proposer_reason: "Project-local constrained fallback"
input_manifest: [specs/skill-proposals/inputs/{slug}.md]
related_notes: []
evidence_packs: []
behavioral_evidence: []
decision: pending
fingerprint: ""
reconsiders: ""
---

# Skill Proposal: {Title}

## Problem

{Repeated task and observed failure or opportunity.}

## Evidence

{Relevant Patterns, Evidence Packs, skill history, and task outcomes.}

## Proposed Change

{One atomic skill creation or update with trigger, ordered actions, decisions, output, and failure handling.}

## Applicability

{Why this is procedural and reusable; scope boundaries and overlap analysis.}

## Behavioral Validation

Candidate paths: [.scratch/{skill-name}]

{Predeclared invariant scenario, observable criterion, baseline, candidate, and evidence-pack paths.}

## Risks

{Overfitting, regression, retrieval, safety, and maintenance risks.}

## New Evidence

{Required only when reconsidering an equivalent rejected proposal.}
