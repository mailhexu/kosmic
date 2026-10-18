---
type: reference
status: draft
audience: both
artifact_role: knowledge
math_provenance: missing
math_provenance_reason: "magnon-mediated-chiral-phonon-splitting.md display math requires one MathDoc marker per equation"
---

# Magnon-Mediated Chiral-Phonon Splitting

---
confidence: 0.95
created: 2026-08-25
last_validated: 2026-08-25
validation_procedure: "Compare the coupled-mode equations and mechanism claims against Cui et al. Nature Communications 14, 3396 (2023), Ren et al. Physical Review X 14, 011041 (2024), Zhang et al. Science Advances 12, eaed7081 (2026), and epcdownfolding/main.tex."
project: epcdownfolding
status: validated
validated_by: automatic
tags: [magnon-phonon-coupling, chiral-phonons, magnon-polarons, spin-lattice-coupling, spin-orbit-coupling]
related_notes: [co3sn2s2-mbc-vs-epc-downfolding]
---

## Conclusion

Yes. Chiral magnons can split a chiral-phonon pair through **helicity-selective magnon–phonon hybridization**. This is a dynamical self-energy or avoided-crossing effect, not an ordinary static force-constant correction.

The splitting is not automatic. The magnon and phonon must share crystal momentum and compatible magnetic-space-group symmetry; the spin-lattice Hamiltonian must contain a bilinear one-magnon/one-phonon term; and the two phonon helicities must acquire unequal self-energies. If opposite helicities have equal magnon energies and equal coupling magnitudes, both phonons shift equally and remain degenerate.

For this project, the demonstrated isotropic derivative $dJ^{\mathrm{iso}}/du$ does **not** provide such a bilinear coupling around a stationary collinear state. The same EPC-downfolding strategy could provide it after a relativistic extension to off-diagonal exchange, DMI, and anisotropy derivatives.

## Minimal coupled-mode model

Let $b_s$ annihilate a phonon and $a_s$ a magnon in helicity or pseudoangular-momentum sector $s=\pm$. In a rotating-wave approximation,

$$
H_2
=
\hbar\sum_{s=\pm}
\left[
\omega_{\mathrm p} b_s^\dagger b_s
+
\omega_{\mathrm m,s}a_s^\dagger a_s
+
\left(g_s a_s^\dagger b_s+g_s^*b_s^\dagger a_s\right)
\right].
$$

For each symmetry-allowed sector,

$$
\Omega_{s,\mathrm{upper/lower}}
=
\frac{\omega_{\mathrm p}+\omega_{\mathrm m,s}}{2}
\pm
\sqrt{
\left(\frac{\omega_{\mathrm p}-\omega_{\mathrm m,s}}{2}\right)^2
+
|g_s|^2
}.
$$

At resonance, the anticrossing gap is $2|g_s|$. In the detuned regime, the phonon-like self-energy is approximately

$$
\delta\omega_{\mathrm p,s}
\simeq
\operatorname{Re}
\frac{|g_s|^2}
{\omega_{\mathrm p}-\omega_{\mathrm m,s}+i\kappa_{\mathrm m,s}},
$$

and therefore

$$
\Delta\omega_{\mathrm p}
\simeq
\operatorname{Re}
\left[
\frac{|g_+|^2}
{\omega_{\mathrm p}-\omega_{\mathrm m,+}+i\kappa_{\mathrm m,+}}
-
\frac{|g_-|^2}
{\omega_{\mathrm p}-\omega_{\mathrm m,-}+i\kappa_{\mathrm m,-}}
\right].
$$

A magnetic field can create the required inequality through Zeeman splitting of opposite-chirality magnons. Magnetic order can also make $g_+\ne g_-$ or remove one helicity channel. Near resonance, the observed modes are magnon polarons rather than pure phonons.

## Microscopic spin-lattice term

Use the tensor exchange expansion

$$
H_{\mathrm{SLC}}^{(1)}
=
-
\sum_{IJ,a,\alpha\beta}
O_{IJ,a}^{\alpha\beta}
 u_a S_I^\alpha S_J^\beta,
\qquad
O_{IJ,a}^{\alpha\beta}
=
\frac{\partial J_{IJ}^{\alpha\beta}}{\partial u_a}.
$$

For a collinear state along $z$,

$$
S^x\simeq\sqrt{\frac S2}(a+a^\dagger),
\qquad
S^y\simeq-i\sqrt{\frac S2}(a-a^\dagger),
\qquad
S^z=S-a^\dagger a.
$$

Consequently:

- $u\,(\partial J^{\mathrm{iso}}/\partial u)\,\mathbf S_I\!\cdot\!\mathbf S_J$ has no term linear in a magnon. It produces a constant plus terms with two magnon operators.
- $u\,(\partial J^{xz}/\partial u)S_I^xS_J^z$ and $u\,(\partial J^{yz}/\partial u)S_I^yS_J^z$ are linear in a transverse magnon.
- DMI derivatives, single-ion-anisotropy derivatives, or noncollinearity can produce analogous linear terms.

After projection onto phonon and magnon eigenvectors, the circular coupling contains the symmetry-sensitive combination

$$
g_\pm
\propto
\sum_a e_{a,\pm}
\left(O_a^{xz}\pm iO_a^{yz}\right),
$$

with site, bond, and Bloch phase factors understood. Symmetry can force one of these combinations to vanish.

## Proven example: FePSe3

Cui *et al.* observed chirality-selective hybridization in the zigzag antiferromagnet FePSe$_3$.

- Two nearly degenerate linear phonons $P_1$ and $P_2$ form circular combinations $P_\pm$.
- Opposite-chirality antiferromagnetic magnons are denoted $M_\alpha$ and $M_\beta$.
- Space-group symmetry makes the two linear-mode couplings real and imaginary, respectively.
- The resulting selection rule is $P_+\leftrightarrow M_\alpha$ and $P_-\leftrightarrow M_\beta$, with the crossed couplings zero.
- The calculated couplings are $2.00$ and $2.16\ \mathrm{cm}^{-1}$; the measured hybridization gap reaches $0.25$ meV.
- A magnetic field Zeeman-splits the two magnon branches, producing unequal shifts of the two phonon helicities.

Their first-principles workflow obtained magnetic derivatives from displaced structures and TB2J. This is an unusually direct benchmark for EPC downfolding: compute the required $O^{xz}$ and $O^{yz}$ from a relativistic EPC dataset, then reproduce the field-dependent magnon-polaron branches without repeated displaced magnetic calculations.

## Relation to the current epcdownfolding method

The manuscript already gives a general Green-function route to derivatives of isotropic exchange, anisotropic exchange, and DMI. The reported implementation and SrMnO$_3$ demonstration retain only $dJ^{\mathrm{iso}}/du$ in a collinear system without SOC.

A practical extension for chiral hybridization needs:

1. fully relativistic spinor Wannier Hamiltonians and EPC vertices;
2. $\partial J^{xz}/\partial u$, $\partial J^{yz}/\partial u$, and all symmetry-related tensor/DMI/anisotropy derivatives;
3. a stable magnetic ground state and its magnon frequencies and eigenvectors;
4. projection of real-space derivatives onto phonon and magnon Bloch modes;
5. construction and diagonalization of the full bosonic dynamical or Bogoliubov matrix, including counter-rotating terms when required;
6. linewidths or a retarded self-energy when comparing with spectra;
7. checks under magnetization or field reversal, symmetry operations, and basis rotations within degenerate phonon subspaces.

## Why this does not replace molecular Berry curvature

Ren *et al.* formulate coupled spin and lattice dynamics using generalized Hessian and Berry-curvature blocks:

$$
M\ddot q=-Kq+G\dot q,
\qquad
q=(u,s).
$$

The exchange derivatives above contribute to the mixed potential block $K^{(\mathrm{sp})}$. Magnon precession requires $G^{(\mathrm{ss})}$. Direct molecular Berry curvature is $G^{(\mathrm{pp})}$, and a complete electronic response may also include mixed Berry blocks $G^{(\mathrm{sp})}$ and $G^{(\mathrm{ps})}$.

Therefore, an EPC-downfolded spin-lattice Hamiltonian can predict selective magnon–phonon hybridization, but $dJ/du$ is not the complete time-reversal-odd lattice response. Direct electronic MBC and magnon-mediated hybridization are complementary mechanisms and can coexist.

## Co3Sn2S2 distinction

The mechanism is physically possible in general but is not the mechanism assigned to the reported Co$_3$Sn$_2$S$_2$ doublets. Zhang *et al.* cite the measured spin-excitation spectrum to rule out **resonant** magnon–phonon coupling in this material. Their Raman-active $E_g$ splitting is assigned to direct electronic MBC; most of the observed infrared $E_u$ peak separation is assigned to Fano interference.

A magnon-mediated calculation for Co$_3$Sn$_2$S$_2$ would still be useful as a quantitative upper bound or complementary self-energy channel, but it should not be claimed as a reproduction of the published mechanism without contrary spectral evidence.

See [[co3sn2s2-mbc-vs-epc-downfolding]] for the full comparison.

## Primary sources

1. J. Cui *et al.*, “Chirality selective magnon-phonon hybridization and magnon-induced chiral phonons in a layered zigzag antiferromagnet,” *Nature Communications* **14**, 3396 (2023). [DOI](https://doi.org/10.1038/s41467-023-39123-y)
2. S. Ren *et al.*, “Adiabatic Dynamics of Coupled Spins and Phonons in Magnetic Insulators,” *Physical Review X* **14**, 011041 (2024). [DOI](https://doi.org/10.1103/PhysRevX.14.011041) · [arXiv](https://arxiv.org/abs/2307.05668)
3. S. Zhang *et al.*, “General ab initio framework for electronic-order-induced lattice-dynamics symmetry breaking,” *Science Advances* **12**, eaed7081 (2026). [DOI](https://doi.org/10.1126/sciadv.aed7081) · [Open full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13281796/)
4. C. Liu *et al.*, “Spin Excitations and Spin Wave Gap in the Ferromagnetic Weyl Semimetal Co$_3$Sn$_2$S$_2$,” *Science China Physics, Mechanics & Astronomy* **64**, 217062 (2021). [DOI](https://doi.org/10.1007/s11433-020-1597-6) · [arXiv](https://arxiv.org/abs/2006.07339)
5. Local manuscript: `epcdownfolding/main.tex`, especially its spin-lattice Hamiltonian, generalized exchange mapping, and discussion of the current no-SOC isotropic implementation.
