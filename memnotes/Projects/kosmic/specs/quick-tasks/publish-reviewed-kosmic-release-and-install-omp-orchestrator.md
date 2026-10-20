---
project_id: "kosmic"
subproject_id: null
record_kind: "quick-task"
local_id: "publish-reviewed-kosmic-release-and-install-omp-orchestrator"
status: done
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
release_commit: "1cabfafaf0f1095305d2619bec42d2bc58e84f1b"
push_remote: "origin"
push_target: "refs/heads/main"
install_adapter: "omp"
install_target: "/home/hexu/.omp/agent/skills/kosmic"
review_base: "1cabfafaf0f1095305d2619bec42d2bc58e84f1b"
review_round: 1
completion_observations: [{"criterion":"origin/main contains the reviewed release by a non-forced fast-forward push; remote identity is observed and local user state is preserved.","observation":"A non-forced push fast-forwarded origin/main from c52ab6a15b2dab0df9cbd450a76fcdc386612cdb to reviewed release1cabfafaf0f1095305d2619bec42d2bc58e84f1b; git ls-remote observed the exact release. Detached local HEAD stayed906c0ab716dc3da33d9ddeaee21bf3b9db5b413c and dirty-file count stayed490 during push.","source":"PushReviewedRelease actual git push/ls-remote output"},{"criterion":"The OMP kosmic package matches the reviewed release's tracked skills/ files and modes, and the prior installation is preserved outside the skill registry.","observation":"The full OMP kosmic directory was replaced from the reviewed Git archive. Independent parent verification matched all64 tracked files, all content hashes and executable modes, with zero missing/extra/mismatched files. Prior62-file installation is preserved at /home/hexu/.omp/agent/skill-backups/kosmic-before-1cabfaf-20261020T122604Z.","source":"InstallOmpKosmic pre/post manifests and backup; parent independent Git-blob hash/mode comparison"},{"criterion":"Installed direct/Python CLI help, work prepare-completion help, and required procedure-skill checks execute successfully; activation is distinguished from on-disk installation.","observation":"Installed direct and Python-prefixed CLI help exited0 and matched under Python3.13.7; work prepare-completion --help and check-required-skills --adapter omp also exited0. This proves on-disk readiness only; current OMP activation is not claimed and reload/new session is required.","source":"Installed CLI smoke output from InstallOmpKosmic"},{"criterion":"Actual deployment observations and independent bounded Standards/Spec decisions are recorded, with no completed Story or prior receipt edits and managed staging cleaned after publication.","observation":"No source implementation changed. The governing record is sole-parent-written and pre-existing Story/receipt files and user index are protected; actual independent decisions are recorded in completion_review. Native receipt publication and managed staging finalization are subsequent bounded transactions, not pre-claimed here.","source":"Parent deployment record, independent bounded review and native publication/cleanup outputs"}]
completion_review: {"reviewer":"Main (deployment coordinator)","axes":{"standards":{"reviewer":"DeploymentStandardsReview","decision":"approved"},"spec":{"reviewer":"DeploymentSpecReview","decision":"approved"}},"decision":"approved","review_base":"1cabfafaf0f1095305d2619bec42d2bc58e84f1b","reviewed_revision":"44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a","findings":[],"scope":["project:specs/quick-tasks/publish-reviewed-kosmic-release-and-install-omp-orchestrator.md","project:specs/INDEX.md"]}
registration_root: "/home/hexu/projects/myagentskills/kosmic/.tmp/kosmic/runs/20261020T122604Z-push-install-omp-767eff3101cc24bfe25b9d305b3bddc3/scratch/writer"
registration_outputs: [".kosmic/working-directories.json","worktree:.kosmic/workdir.json"]
---

# Publish reviewed Kosmic release and install OMP orchestrator

## Request and Approval

The user explicitly requested “git push, and install the skill to omp”. This approves the bounded release/install plan below; no source implementation or shared-library migration is authorized.

## Scope and Adapter Plan

- Push reviewed commit 1cabfafaf0f1095305d2619bec42d2bc58e84f1b to origin/main without force. Remote main was observed at c52ab6a15b2dab0df9cbd450a76fcdc386612cdb, an ancestor of this release. Preserve detached local HEAD, local branches, index, and unrelated working files.
- Install exactly this commit's tracked skills/ package as the OMP orchestrator at /home/hexu/.omp/agent/skills/kosmic, following docs/installation.md's whole-directory update contract. Preserve package structure and executable bits; do not hand-edit installed skill content.
- Validate a staged package before replacing the existing kosmic package. Retain the old installed package outside OMP's skill-discovery directory, and preserve all other skills, configuration, vaults and the Shared Skill Router.
- Authorize disposable managed staging, a private record-only writer and its registration/configuration, this record, derived STATUS, specs-index row and native completion log. Deployment agents do not edit the record; the parent is its sole writer.

## Out of Scope

New source changes, force-pushes, rewriting local history, installing other adapters or project skills, modifying global vaults, and claiming activation in an already-running OMP session.

## Acceptance Criteria

- [ ] origin/main contains the reviewed release by a non-forced fast-forward push; remote identity is observed and local user state is preserved.
- [ ] The OMP kosmic package matches the reviewed release's tracked skills/ files and modes, and the prior installation is preserved outside the skill registry.
- [ ] Installed direct/Python CLI help, work prepare-completion help, and required procedure-skill checks execute successfully; activation is distinguished from on-disk installation.
- [ ] Actual deployment observations and independent bounded Standards/Spec decisions are recorded, with no completed Story or prior receipt edits and managed staging cleaned after publication.

## Routine Decision

No new reusable procedure mechanics or uses_routines edges. This deploys an already-reviewed release using the existing documented package-install contract.
