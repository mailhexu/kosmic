---
type: Domain Topic
id: docs-papers/usage/symphon-release
domain: docs-papers
audience: usage
artifact_role: guideline
status: draft
summary: Release symphon to PyPI and maintain its phonopy 4.x and spgrep-modulation compatibility state.
triggers: [symphon release, pypi upload, phonopy 4 compat, spgrep-modulation]
source_project: native
source_sha256: empty
aliases: [symphon pypi, symphon compat]
---

# symphon Release and phonopy 4 Compatibility

## Release steps

1. Bump `version` in `pyproject.toml`.
2. Run `rm -f dist/* && uv build`.
3. Validate metadata before upload. Unzip the wheel METADATA. Assert no `@`
   direct URL appears in `Requires-Dist`; PyPI rejects PEP 508 direct
   references, so never pin git dependencies. Assert `symphon/_compat.py`
   is in the wheel namelist.
4. Upload with `python -m twine upload --repository pypi dist/*`.
5. Verify through the PyPI JSON API at
   `https://pypi.org/pypi/symphon/json`. `pip index versions` can serve a
   stale cache right after upload.

## phonopy 4.x compatibility state

- Requirements: `phonopy>=4.1.0` and `spgrep-modulation>=0.3.0`. The
  released spgrep-modulation 0.3.0 is import-broken with phonopy 4; only
  upstream commit ceb5a229 has the fix, and it is unreleased.
- `symphon/_compat.py` aliases the moved `get_eigenvectors` back onto
  `phonopy.phonon.degeneracy`. `symphon/__init__.py` and
  `tests/conftest.py` activate it. Delete the shim when a
  spgrep-modulation release contains ceb5a229.
- The `PhonopyAtoms` keyword is `magnetic_moments`, not `magmoms`, and the
  class rejects `pbc`.
- Any non-None `magnetic_moments`, even all-zero defaults, switches
  `Symmetry` to `SpglibMagneticDataset`. Its rotations arrive in
  time-reversal pairs, `is_primitive_cell` becomes False, and a spurious
  Non-primitive-cell RuntimeError follows.
  `abipy_io.ase_atoms_to_phonopy_atoms` drops moments below
  `_MAGMOM_ZERO_TOL = 1e-6` muB; keep that guard.

## Gotchas

- Identify daughter space groups with spglib `symprec=1e-6`. At `1e-5`,
  residual noise yields phantom daughters. Production
  `irreps_anaddb.py` still uses `1e-5`; tightening it changes CLI golden
  references.
- The sg142 CLI fixture exceeds 120 s once modulation paths run. Test
  subprocess timeouts are 900 s; the full suite takes about 27 min.
- Genuinely magnetic PHBST structures still break the irreps path.
