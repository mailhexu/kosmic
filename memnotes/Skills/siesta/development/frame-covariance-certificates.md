---
type: Domain Topic
id: siesta/development/frame-covariance-certificates
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Certify SIESTA SOC and +B frame covariance (z vs x) with exact metric-covariant rotated-DM or clean re-init one-shot protocols; oracle-fixture debugging and sisl/scipy traps.
triggers: [frame covariance certificate, rotated dm certificate, one-shot frame test, op frame covariance]
source_project: native
source_sha256: empty
aliases: [rotated dm certificate, soc frame certificate]
---

# Frame-Covariance Certificates (z vs x)

Use when a perspin_DFTB computation changes under a spin/frame rotation
and a convention or sign defect is suspected.
## Fixtures and seed machinery
- 2-atom primitive SmN: C4 maps z to x with identical ions; E_x = E_y =
  E_z exactly. Isolated atom next; TmFeO3 last. 8-atom cells need
  cubic-op-consistent InitSpin pairings (basins 350 meV apart).
- Spin-only rotation (I x W) is exactly S-unitary; default seed tool.
  Orbital-sector rotations of a dense solid DM are unrepresentable.
- Gate every seed: Tr[D.S] exact, Hermiticity <= 1e-12, file roundtrip,
  correct S/L moments; right spin factor W+ everywhere.
## Exact metric-covariant rotated-DM certificate (SOC)
1. Converge the z reference (gentle mixing w=0.05, history 8; Cold
   smearing 300 K tames the 4f branch); record 1-shot E_KS(1), S, L.
2. Build the rotated DM. Read the DM with the fdf geometry (the bare DM
   file fabricates one atom per orbital). Spatial op Q with Q L = L A
   (integer A, sympy), atom shifts t. Per supercell cell assemble the
   dense spinor M[k] (sisl map M11r=0, M22r=1, M12r=2, M12i=3, M11i=4,
   M22i=5, M21r=6, M21i=7); M' = W M W+, W = kron(R_orb, U_spin); remap
   image keys n' = A n + t_j - t_i; scatter into the same CSR pattern;
   require 0 misses.
3. Orbital R from the rlylm real-SH convention: fit C by random-angle
   lstsq (`lpmv(m, l, x)` argument order; N inside the sqrt);
   R_l = C+ d^l(theta)^T C (R_orb.T if chirality inverts; explicit
   matmul, not einsum).
4. Certificate run: MaxSCF 1, DELETE the DM.InitSpin block (FixDirection
   re-pins z otherwise). Gates: read Succeeded, Tr[D.S] = Qtot (a
   deficit proves a non-S-unitary seed), S/L rotated with matching
   chirality, Ef about 0.4 meV. E_KS is the comparator; Harris keeps a
   stale Im convention here.
## +B OP certificate: clean per-frame re-initialization
- NEVER frame-rotate OP states with FixDirection DM-restarts or sisl
  spin_rotate: both rotate spin space only; L stays in the old frame.
- Per frame: clean `DM.InitSpin` theta=0 (z) / 90 (x), MaxSCF 300-400;
  with the correct sign the Hund lock forms by iteration 5.
- Use `OP.UseLocalAxis` (LSA); `OP.UseTotalMoment` is unstable for
  zero-moment FM on both operator signs.
- Accept: |L|, |S| to 1e-2 muB, axes rigidly rotated, dE at meV level.
  Reference (SmN2, B=0.5, U=6/J=0.8, LSA+LCap): z E=-2739.6173,
  x -2739.6139, dE 3.4 meV.
## Adjudication gates (they caught two wrong fixes)
- Z-invariance: a fix leaves the z 1-shot E_KS bit-identical; failing
  means wrong form, revert immediately.
- j-multiplet gate: isolated atom, SOC-only; j = l-1/2 below j = l+1/2, degeneracies 2j+1.
- Discipline: build from clean trees; verify the footer banner; ship
  fdf as base64; revert and prune when the oracle rejects; log every
  adjudication.
