---
project_id: "kosmic"
subproject_id: null
status: done
record_kind: "quick-task"
local_id: "publish-native-index-release-and-refresh-omp"
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "e5f3b54e3a481b3db9a665428ab1616e0aeb4671"
review_round: 1
created: "2026-10-24"
updated: "2026-10-24"
completion_observations:
  - criterion: "A non-forced push fast-forwards origin/main to the reviewed release including all three completed Stories; the prior remote is an ancestor, both existing executable CLI modes are retained, and unrelated local HEAD/index/working files remain unchanged."
    observation: "Non-forced push fast-forwarded origin/main fromb386ac967dc7969a45de1a6d756a4c46a7c777cc to78eeedb4ac2a425a281bd6093cdb8f822781bbba. Release retains100755 on both CLI entries; source bytes are unchanged. Original HEAD,15 source bytes/modes, and staged entries/content are preserved. An accidental main-index read-tree was repaired from the pre-command snapshot; cache bytes changed, as fully disclosed in Deployment Incident."
    source: "git merge-base ancestry success; actual git push --porcelain success b386ac9..78eeedb; private-index tree uses original executable modes; actual staged blob/mode comparison and original-source hashes/modes after deployment."
  - criterion: "The installed OMP kosmic package matches every tracked release skills/ file and executable mode, with no stale extra files; the prior target is retained outside skill discovery and unexpected target drift is refused before replacement."
    observation: "Installed all66 tracked release package files with0 missing/extra/hash/mode mismatches. Previous installation retained at/home/hexu/.omp/agent/skill-backups/kosmic-before-78eeedb4-20261024T053250Z. Target identity/content was compared immediately before replacement; checked sibling staging published completely."
    source: "Disposable install_package.py actual result: files66, missing0, extra0, hash_mismatches0, mode_mismatches0, previous_installation_preserved:true, staging_published:true. Complete release package extracted by git archive."
  - criterion: "Actual installed direct/Python CLI entry and native spec creation/preparation execute successfully from a disposable Project; existing required OMP procedure skills resolve, and on-disk readiness is distinguished from activation after reload."
    observation: "Actual installed executable resolved required OMP skills and created a native Quick Task with non-null operation_id; Python-prefixed explicit-writer preparation preserved blank observations and all Project/writer bytes with caller optional Git locks enabled. On-disk readiness only; current-session activation is not claimed."
    source: "Actual installed smoke_installed.py EXIT0; direct check-required-skills output required skills available for omp; native identityinstalled-smoke/quick-task/installed-native-preparation; read-only preparation source_revision2dd2e17c1808f4e91e53cad851c1b9b44afd02b8c2fa7c4e364ae8b238233966."
  - criterion: "Actual release/install observations and two independent bounded Standards/Spec approvals are recorded before native completion; prior completed records/receipts remain unchanged and owned staging is cleaned."
    observation: "Actual deployment observations and the index incident are embedded here. CreationStandardsScout and CreationSpecResume independently approved the first complete deployment pair on held revision170bc1e1...; the recorded review below precedes native finish. Installer staging was removed by publication; remaining managed workspace cleanup follows receipt preservation. No prior completed record or receipt was edited."
    source: "Both actual independent reviewer decisions accepted staged-content restoration with the explicitly disclosed index-cache caveat; completion_review records their real identities and decisions. Installer staging_published:true; managed run lifecycle owns final disposal."
completion_review:
  reviewer: "Main"
  axes:
    standards:
      reviewer: "CreationStandardsScout"
      decision: "approved"
    spec:
      reviewer: "CreationSpecResume"
      decision: "approved"
  decision: "approved"
  review_base: "e5f3b54e3a481b3db9a665428ab1616e0aeb4671"
  reviewed_revision: "170bc1e12291e04493e610670a0ea41d67fc10917339f6fdb0193ee08d43b9fd"
  scope:
    - "worktree:skills/scripts/kosmic_project_skills.py"
    - "worktree:skills/scripts/kosmic_curation.py"
    - "project:specs/quick-tasks/publish-native-index-release-and-refresh-omp.md"
    - "project:specs/INDEX.md"
  findings:
    - id: "DEP-A1"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "Disposable installer prints zero mismatch counters after exact-equality verification rather than incrementally measuring counters; verification raises before reporting any mismatch."
    - id: "DEP-A2"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "Release installation equality covers tracked file paths, modes and bytes, not directory-mode equality."
    - id: "DEP-A3"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "Package retains already-repo-tracked __pycache__ files; changing tracking policy is outside this release."
---

# Publish native-index release and refresh OMP

## Approval and Scope

The user selected “Publish and install OMP” after the three native-index/fingerprint Stories completed. Publish their reviewed implementation and already-reviewed lean workflow prerequisites to `origin/main` by a non-forced fast-forward. Install the exact release's complete tracked `skills/` package at `/home/hexu/.omp/agent/skills/kosmic`, preserving the previous installation outside skill discovery. Preserve existing executable modes for `kosmic_project_skills.py` and `kosmic_curation.py` in the release tree; the private implementation snapshot flattened those modes. Do not change their contents or the user's original working-tree modes.

No force push, reset, stash, unrelated working-tree/index changes, Shared Skill Router refresh, unrelated skill/config edits, feature changes, historical pin rewriting, or activation claim in the current session. The private implementation history remains preserved. Use a clean isolated writer and managed staging. No new routine or note: this executes the existing installation procedure.

## Acceptance Criteria

- [ ] A non-forced push fast-forwards origin/main to the reviewed release including all three completed Stories; the prior remote is an ancestor, both existing executable CLI modes are retained, and unrelated local HEAD/index/working files remain unchanged.
- [ ] The installed OMP kosmic package matches every tracked release skills/ file and executable mode, with no stale extra files; the prior target is retained outside skill discovery and unexpected target drift is refused before replacement.
- [ ] Actual installed direct/Python CLI entry and native spec creation/preparation execute successfully from a disposable Project; existing required OMP procedure skills resolve, and on-disk readiness is distinguished from activation after reload.
- [ ] Actual release/install observations and two independent bounded Standards/Spec approvals are recorded before native completion; prior completed records/receipts remain unchanged and owned staging is cleaned.

## Deployment Incident

Before any push or installation, the coordinator accidentally invoked `git read-tree e5f3b54...` without the intended private `GIT_INDEX_FILE`, replacing the main index only. HEAD and working files were untouched. The managed run's pre-command porcelain-v2 snapshot identified the original staged state: HEAD plus the modified `memnotes/Projects/kosmic/log/kosmic-2026-10-13.md` blob `d45acb71c05ade6fc407ea5d57e314a91c7a9922`, mode100644. There were no index renames or unmerged entries;112 rename records were worktree-only (`.R`). A private index reconstructed that tree, then restored the main index. Actual `git diff --cached --raw --no-abbrev` matched exactly the captured staged blob/mode and HEAD remained906c0ab716dc3da33d9ddeaee21bf3b9db5b413c. Index cache bytes differ from the original; preservation means the staged entries/content, not byte-identical cache representation. The user was notified before continuing. All subsequent Git-index preparation uses explicit `env GIT_INDEX_FILE=...`; no original working-file modes or contents are changed.

## Routine Decision

This release executes the existing documented package-install/update procedure. It introduces no reusable deterministic mechanics or routine edges, so `routine_decision_required: false`; no new Task P proposal or routine publication is warranted. This is the same no-new-routine reason already declared in Approval and Scope, placed under the validator's required heading after the first finish refused its missing location.

