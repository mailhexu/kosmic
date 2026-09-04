---
project_id: kosmic
working_state: working-tree
---

# kosmic

## Overview
Kosmic is a knowledge-oriented, spec-driven AI-agent skill: a Markdown workflow orchestrator plus a deterministic Python Projection CLI that derives an atomic Usage/Development Skill Pair per Project from an authoritative OKF v0.2 notes bundle.

## Tech Stack
- Markdown (skill instructions, templates, vault knowledge)
- Python 3.11+ standard library (Projection CLI)

## Directory structure
kosmic/
├── README.md — repository overview and installation
├── CONTEXT.md — domain language for Project Knowledge and Skill Projection
├── docs/ — user documentation, ADRs, research, specs
├── skills/ — the distributed skill package (SKILL.md, references/, scripts/)
├── tests/ — Projection CLI tests
├── assets/ — workflow diagram
└── memnotes/ — this Kosmic vault (project data, not part of the installed skill)

## Knowledge Base
- [Project Knowledge index](notes/index.md)
- [Notation Reference](notes/notation.md)

## Project Skills
- Usage: `skills/kosmic-usage/` (publication deferred until stable usage notes exist)
- Development: `skills/kosmic-development/` (publication deferred until stable usage notes exist)

## Recent Activity
- [Latest Session](log/kosmic-2026-09-02.md)
