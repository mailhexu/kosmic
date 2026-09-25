---
okf_version: "0.2"
---

# ABINIT Scoped MPI Knowledge

This bounded Project owns only source provenance and future evidence for MPI CG-reduction guidance.

## Scope

- [Scoped Project boundary](scoped-project-boundary.md) — stable authority boundary; not operational guidance.

## Development

- [MPI distribution invariants](mpi-distribution-invariants.md) — draft guideline for ownership and reduction correctness.
- [MPI topology model](mpi-topology-model.md) — draft knowledge of ABINIT communicator topology.
- [FFT distribution model](fft-distribution-model.md) — draft knowledge of local FFT/G-vector storage.
- [Historical CG-reduction evidence](mpi-cg-reduction-historical-evidence.md) — dated legacy validation; not current execution proof.

## Distilled Guidelines (2026-09-25 consolidation)

* [ABINIT CMake Build from Git](abinit-git-cmake-build.md) - Git checkouts ship no configure; CMake recipes plus the levmar include and cppopts-dumper configure failures.
* [ABINIT Makemake Build Tree Pitfalls](abinit-makemake-build-gotchas.md) - Builds read a mirror source root; copy edits, touch .mod consumers, add public :: or symbols vanish.
* [ABINIT Unit Checker Extension](abinit-checker-unit-test-extension.md) - Checkers need abinit.src/amf registration; fixture hygiene rules keep physics mutations catchable.
* [ABINIT Unit Checker Registration](abinit-unit-checker-registration.md) - Register test_* executables via checkers dict, amf link closure, makemake and config.status regeneration.
* [ABINIT Wave-6 Build and Runtime Validation](abinit-wave6-build-validation.md) - Validate on CMake and makemake; ABI_SFREE, .files line count, and Gamma DFPT acceptance gates.
* [ABINIT on Manneback with Fallbacks](abinit-manneback-fallbacks-cmake.md) - Keira build recipe: m4 and libxc pkg-config fixes, GCC13 stamp skips, nm hard gate.
* [ABINIT Test Baseline Adjudication](abinit-testsuite-baseline-adjudication.md) - Adjudicate census failures against saved baselines; classify drift as T/S/R before regenerating refs.
* [NC DFT+U Derivative-Channel FD Certification](dftu-derivative-fd-cert.md) - Certify new force/stress/response derivative channels against U-on/U=0 central FD: mpw-vs-npw_k stride audit, twin-deck conventions, basin-flip h-convergence, v10 pinning.
* [NC DFT+U Force/Stress Certification Protocol](dftu-force-stress-cert-protocol.md) - BLAS stride audit recipe, variable-npw multi-k FD protocol, stress-chain dL batching, SCF basin-flip adjudication, AFM NiO reference numbers.
* [NC DFT+U Spinor Forces/Stress FD Certification](nc-dftu-forcestress-fd-cert.md) - Spinor force/stress FD certification on develop: fixture validation, inversion-broken bases, exit gates, v10[237] pin, MPI equality close.
* [ABINIT-vs-QE Clamped-Ion Elastic Stress-FD](elastic-strain-fd-cert.md) - Cross-code elastic FD: QE Bernasconi smooth cutoff mandatory, ABINIT ecut>=80 gate, isotropic U-control discriminator, scalar fixture, sign conventions.
* [Finite-U NC DFT+U Oracle Adjudication](finite-u-oracle-adjudication.md) - Validate DFPT observables via finite-displacement and energy-Hessian Phonopy oracles; conservativity checks; NiO Wave-6 sign-flip lesson.
* [Port-vs-Fork DDB Certification (NC DFT+U)](port-vs-fork-ddb-certification.md) - Certify DFPT families against the fork binary: build-mirror sync trap, matched-tolerance twins, family-wise diffs, U0 bitwise control, coverage rules.
* [MPI Equality Certification (NC DFT+U Port)](mpi-equality-certification.md) - Serial-vs-MPI gates without false failures: same-solver references, transient one-step noise bands, port-off/U=0 twins, measured floors.
* [Port-vs-Fork Oracle Provenance Adjudication](port-fork-oracle-provenance-adjudication.md) - Attribute port-vs-fork regressions before editing source: oracle provenance, cross-build A/B, fork archaeology, per-leg source-norm probes, representation-scoped fixes.
* [NC DFT+U Finite-q D2U Residual Attribution](finiteq-d2u-residual-attribution.md) - Slot-key parse rules, U0-gate-first probe order, and the un-audited rho1 U-response residual class for scalar finite-q DDB-vs-FD campaigns.
* [NC+U Elastic Element-Level V2M Adjudication](nc-dftu-elastic-element-adjudication.md) - Localize elastic DDB residuals by comparing V2MF+V2MN element dumps against the occupation-FD oracle; dual dump formats, block keys, and the structurally incomplete psi2-free closure verdict.
* [Wave-8 Term-Level DDB Owner Oracle](wave8-term-level-ddb-oracle.md) - Find which native ledger term owns a failing DFPT+U DDB channel: env-gated audit classes, two-q term regression, negative controls, and build mirror discipline.
* [FD-Oracle Finite-q Alias Trap](fd-oracle-finiteq-alias-trap.md) - Diagnose finite-q residuals that fail closure: supercell-Nyquist alias mechanism, zero-cost Hermitized-target refit, envelope-inert checks, and co-occurring tooling traps.
* [ABINIT Symmetry-Convention Adjudication](symmetry-convention-adjudication.md) - Adjudicate rotation/index-map/Bloch-phase conventions by exhaustive variant scan on discriminating geometry; zarot orientation answer and anti-patterns.
* [NC DFT+U Rotation-Convention Oracle](nc-dftu-rotation-convention-oracle.md) - Symrec-chain overlap identity, adjudicated fork bugs (rotate_overlap_matrix_nc, istwfk=2), and the decisive variant-scan recipe with debug ladder.
* [ABINIT Fixture Bistability Screening](fixture-bistability-screening.md) - Multi-start SCF bistability screen before oracle campaigns: branch-aware comparators, start cures, mixer-sweep limits, and displacement tooling traps.
* [Dual-Tree NC DFT+U Port Protocol](dual-tree-port-protocol.md) - Shared v10 test namespace, per-tree toolchain refs, absolute-dataset restart chains, and envelope-lift bitwise equivalence for pao-proj/develop ports.
* [Noncollinear initspinden Port](noncollinear-initspinden-port.md) - spinat_cart rotation invariants, m_gstate seam, chkinp nspden widening, and the t88 noncollinear DEN-restart regression fixture.
* [NC DFT+U SOC Ground-State Comparison](nc-dftu-soc-ground-state.md) - Matched SOC-on/off two-dataset recipe; useylm and occopt=0 moment-collapse root causes; guarded DFPT scope and validation checklist.
* [NC DFT+U Mixed-Strain Occupation Response (s2 Term)](nc-dftu-strain-response-s2-term.md) - sympy-verified Dudarev s2 term, 2n+1 occupation-matrix boundary, and elementwise V2MF/V2MN-vs-occupation-FD gating.
* [SOC=0 Collinear-vs-Spinor Representation Adjudication](soc0-collinear-spinor-representation-adjudication.md) - Six-step diagnostic ladder (state map, Harris, basin, H2/H3, U=0, trace) and the nspden=4 GGA XC-kernel sign-write-back root cause.
* [Widening a chkinp Input Guard (NC DFT+U Port)](chkinp-guard-widening.md) - Verify the admitting clause empirically, dead-letter route checks, build-WIP diff attribution, and strict commit scope.
* [Orbmag Lambda-Augmentation Stress Channel (ORBMAGAUG)](orbmag-augstress-channel.md) - ABINIT_ORBMAG_AUGSTRESS wiring, atindx1/pawgrnl traps, matched-control FD protocol, and the sign-flipped lambda-coupling verdict.
* [Orbmag Orbital-Moment Constraint Recipe](orbmag-constraint-recipe.md) - constraint_kind 21/22/23 wiring, energy-slot leak fix, FD stress validation, and calibration protocol.
* [ABINIT Env-Gated Probe Diagnosis](env-gated-probe-diagnosis.md) - Isolate numerical defects with disposable env-gated builds and three mandatory bit-level controls.
* [ABINIT Total-Energy Solver-Path Diagnosis](totalenergy-solverpath-diagnosis.md) - Diagnose wfoptalg/npband-only etotal defects via YAML component diffs and serial reproduction.
* [ABINIT ffnl Chain Verification](ffnl-chain-verification.md) - Verify the nonlocal ffnl/stress chain with rank-gated same-kpt triple dumps and verified conventions.
* [ABINIT Campaign Hygiene](campaign-hygiene.md) - Scratch retention, throwaway-tree lifecycle, A/B ref-drift attribution, and disk pressure.
* [ABINIT Instrumented-Dump Recipe](instrumented-dump-recipe.md) - Gated Fortran dump cycle: placement, edit, and parsing traps plus verified nonlocal conventions.
* [ABINIT GGA Finite-Difference Audit Traps](gga-fd-audit-traps.md) - favg and FFT-grid noncovariance traps in GGA DFPT-versus-FD audits; uninitialized-collective fix.
* [ABINIT WFK Unfolding Fixture Generation](wfk-fixture-generation.md) - Two-dataset WFK band-path decks, k-wrapping traps, numeric EBS validation, publication flow.
* [ABINIT G7 DDK Cutover](g7-ddk-cutover.md) - DDK PAO derivative, gh1c ownership, BEC-preserving DDB merge, and validation sequence.
* [ABINIT v10 test workflow](v10-test-workflow.md) - Claiming, authoring, running, pinning, regenerating, and bisecting v10 tests across parallel trees.
