---
type: Domain Topic
id: methods/development/nist-asd-soc-extraction
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Fetch NIST ASD atomic fine-structure levels for the periodic table and extract per-(n,l) one-electron spin-orbit splittings through LS coupling.
triggers: [nist asd, fine structure levels, one-electron soc, lande interval rule, atomic spectra fetch]
source_project: native
source_sha256: empty
aliases: [soc extraction]
---

# NIST ASD Spin-Orbit Coupling Extraction

Fetch National Institute of Standards and Technology (NIST) Atomic Spectra Database (ASD) fine-
structure levels for the periodic table and extract the per-(n,l) one-electron spin-orbit
coupling (SOC) splitting through Russell-Saunders (LS) coupling, for comparison against an all-
electron Dirac descriptor. Tools: `magdescriptor/tools/fetch_nist_fs.py` and
`magdescriptor/tools/extract_nist_xi_nl.py`.

## Fetch raw levels

Query `https://physics.nist.gov/cgi-bin/ASD/energy1.pl` with `spectrum=SYMBOL I` (neutral atom;
example `Al I`), `units=1` (eV), `format=0`, `page_size=200`, and the configuration, term,
level, and J outputs on. Parse the HTML table rows (four columns: configuration, term, J,
level); forward-fill configuration and term; the first configuration block is the ground
configuration. Parsing traps:

- Bracketed energies: cells wrap derived values as `[0.00000000]`. Take the first numeric token.
  Do not regex-strip the brackets; the strip deletes the ground state (it removed all He I
  levels in one case).
- J fractions: split `1/2,3/2` only on `[,;]` and ` or `. Never put `/` in the delimiter set;
  `1/2` then becomes `1.0`. Tokenize configurations on `(\d)([spdfg])` boundaries so occupancy
  digits do not merge into the next n.

Store ground configuration, open shell (n,l), all ground-term J levels, the fine-structure
splitting dE_FS, and all ground-configuration terms; output `nist_fs.json`.

## Extract one-electron zeta_nl

NIST publishes term energies; the one-electron splitting is derived. Parse LS terms `^(2S+1)L`
into S and L; skip L=0 half-filled terms (p3, d5, f7) and jj labels like `(1/2,1/2)`. Fit the
Lande interval rule by linear regression of E(J) on `x = [J(J+1)-L(L+1)-S(S+1)]/2`; the slope
is the term zeta. The stretched-determinant derivation gives `|zeta_nl| = |zeta_term| x 2S` and
a j splitting `delta_eps = zeta_nl (2l+1)/2`; for single-valence-electron atoms this equals
dE_FS exactly and matches the all-electron descriptor. Flag multiplets with irregular Lande
intervals (ratio above 1.5) as intermediate coupling and approximate; output `nist_xi_nl.json`.

## Half-filled or L=0 ground terms and plots

No ground-term fine structure exists there. Extract zeta from an excited term of the same
configuration (the ion stays neutral, so no screening shift enters; the excited term needs an
LS coefficient), or use an ion stage where the shell is not half-filled (example: Bi 6p3 ^4S to
Bi2+ 6p1 ^2P); ion zeta_nl exceeds the neutral value through reduced screening, so treat it as
an overestimate. For plots, `plot_nist_fs_periodic_table.py` shows the assumption-free dE_FS
and `plot_nist_xi_periodic_table.py` shows the LS one-electron splitting comparable to all-
electron data; gray marks s-only or closed shells and half-filled or jj cases, and a tilde
marks intermediate-coupling estimates.
