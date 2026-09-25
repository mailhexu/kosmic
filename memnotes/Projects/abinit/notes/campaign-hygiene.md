---
type: Project Knowledge
title: ABINIT Campaign Hygiene
description: Scratch retention, throwaway-tree lifecycle, A/B ref-drift attribution, and disk-pressure procedures for delegated ABINIT campaigns.
confidence: 0.8
created: '2026-09-25'
updated: '2026-09-25'
validation_procedure: "Apply the retention sweep and A/B attribution on the next delegated campaign; verify no evidence loss."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, campaigns, scratch, ref-drift, disk]
---

# ABINIT Campaign Hygiene

## Scope

Apply these procedures to every delegated ABINIT campaign in this workspace. The procedures are proven across the
2026-09-18 campaign chain: story-550, gap-#7 A/B/C, W8 prerequisites, choice-6.

## Scratch retention

Keep evidence files: `*.abi`, `*.abo`, `*DDB*`, finite-difference (FD) oracle files (interatomic force constant
`npy`, `fd_dynmat` machinery), `analysis/*.json`, `CROSSCHECK*.md`, generator and analyzer scripts, ledger logs,
saved diffs. Delete regenerable files: `*.nc` (OUT, GSR), `*WFK`, `*DEN`, `*.agr`, `*.stderr`, and raw `*.stdout`
larger than 2 MB. Instrumented builds flood stdout; the parsed audit evidence lives in the analysis JSON files,
not in the raw log. Sweep only your own campaign directories; never sweep a sibling lane's directories. Run:

`find <dirs> -type f \( -name "*.nc" -o -name "*.agr" -o -name "*WFK" -o -name "*DEN" -o -name "*.stderr" \) -delete`

then `find <dirs> -name "*.stdout" -size +2M -delete`.

## Throwaway-tree lifecycle

1. Implement and certify in `abinit-<wave>-src/` with `build-<wave>/`. These are copies; never work in the live tree.
2. Prove the OFF control bitwise by derivatives-database (DDB) md5 before production runs. Re-verify after every source edit.
3. Match the optimization flags of the reference build. Once, `-O3` instead of `-O2` broke bitwise identity at 3.9e-4.
4. On a pass, apply the diff to the live tree. Rebuild. Re-run the failing subset as an A/B per the next section. Pin tests. Only then commit.
5. After landing, delete the throwaway build tree and the source copy when the diff is committed and archived. Keep the source copy only when its env-gated instrumentation is the ready-to-use harness for a known next wave.

## A/B ref-drift attribution

The develop suite is chronically red from toolchain drift. References were pinned on v10.9.3.1 and v10.9.3.2
builds against the current v10.9.3 header. Typical drift: etotal shifts near 1e-12 Ha, DDB records near 4e-9
absolute, `.abo` line-count drift. Before you blame your change, attribute the failure set:

1. Revert only the suspect change. Rebuild. Re-run the failing subset.
2. Same failures: the drift is pre-existing and your change is inert. Verify the run paths; for example `useylm=1` routes to `nonlop_ylm`, not `nonlop_pl`.
3. New or different failures: your change owns them. Investigate.

Never regenerate references as a side effect of a foreign lane's test. References are pinned per toolchain; the owner of a physics change owns its reference regeneration.

## Hub-agent discipline

Resume a failed task agent with `hub send`; the agent keeps its transcript. Send one steering message: name the
inconsistency, state the boundary, restate the deliverable. A working campaign contract: work confined to
`scratch/<campaign>/` plus throwaway trees; a headline JSON with explicit verdict fields; "honest verdict or
blocker" as acceptance; an explicit writes-confined declaration. A/B decisions on pinned refs and commits belong
to the orchestrator, not the agent.

## Disk pressure

`/home` sits at 99%. Check `df -h /home` before every long campaign. Sweep your own finished campaigns. Warn the sibling lane when free space drops below about 20 GB; detached runs die mid-write.
