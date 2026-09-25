---
type: Domain Topic
id: siesta/development/op-sign-oracle
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Adjudicate the SIESTA +B orbital-polarization operator sign via SCF dynamics and the Hund oracle; the trace/func diagnostic is sign-blind.
triggers: [op sign, orbital polarization sign, quench vs lock, OP_ENERGY_DIAGNOSTIC]
source_project: native
source_sha256: empty
aliases: [op operator sign, vb sign]
---

# +B OP Operator-Sign Adjudication

Use when +B SCF dynamics oscillate, orbital moments run away, or MAE
signs look wrong.
## Critical caveat: the trace/func oracle is SIGN-BLIND

Under the branch's conjugate-compensated conventions,
`OP_ENERGY_DIAGNOSTIC trace==func` passes identically for BOTH global
signs of V_B (verified at B=+0.5 and B=-0.5, 8-digit equality). It
validates internal consistency only; it cannot adjudicate the physical
sign. Relying on it caused the f8258cc05 sign flip (2026-09-01): every
OP SCF at B>0 quenched L. Fixed in `a23c0d21a` (Bpot=Bval=-B, LCap ON).
With the correct sign the diagnostic reads `trace == -func`; `func` is
negative at the locks — a consistency fingerprint, not a sign oracle.
A constant rational trace/func ratio means an operator-vs-functional
flip. Energy checks cannot see the sign: E^OP = -B|L|^2 is even under
L -> -L.
## The valid adjudicator: SCF dynamics (Hund-rule physical oracle)

Correct sign gives positive feedback: L LOCKS. Wrong sign gives negative
feedback: +/-L bouncing then damped quench. Decisive cheap protocol, all
on the ion:
1. Fixture: isolated Sm3+ f5 (NetCharge 3.0), LSA, FixDirection T, linear mixer weight 0.05, MaxSCF 300.
2. Extract per-iteration Lz/Sz from out.log (`Magnetic moments from
   orbital angular momenta` species Total rows; Mulliken S from the
   `mulliken:` table; per-orbital rows carry an extra orbidx column).
3. LOCK: Lz monotone to about -4, S = +5.0, dD < 2e-4 -> sign CORRECT.
   LCap is needed (gain > 1); without it the run runs away to |L| about
   8.5 f4-d states.
4. BOUNCE->QUENCH: |L| oscillates +/-4.2, ends |L| about 0.11 -> sign
   INVERTED.
5. Solid cross-check: SmN 2-atom LSA B=0.5 U=6 J=0.8 — correct sign locks
   by iteration about 5 and relaxes to the zero-moment FM (L=-4.2,
   S=+5.1), E_KS about -2739.6, E_OC = -12.5 eV/atom; wrong sign
   quenches to L about 0.06 and printed low energies of lock visits are
   inconsistent-(H,DM) artifacts. Locked solid sits about 12.4 eV below
   the quenched basin with negative func.

Fixtures (nic6): `/scratch/hexu/siesta-tests/sm-cascade/`; full evidence
chain in `memnotes/Projects/siesta/log/siesta-2026-09-06.md`.
## Sign chain reference (m_pot_dftu.F90)
- `int_so_ang(first,second)` gives real antisymmetric tables; true L:
  Lx = -iL(3), Ly = iL(2), Lz = iL(1).
- Reversed V storage is undone by the swapped int_so_ang call + conjg
  and 3<->4 swap at the Vi->H fold-in. Do NOT add a global -B on top
  (that was the pre-f8258cc05 bug).
- Correct total-moment V_B pattern: 2iB(L3 Mx - L2 My - L1 Mz).
