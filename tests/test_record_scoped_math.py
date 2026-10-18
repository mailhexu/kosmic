"""Record-scoped math completion and named check-math regression scenarios.

Approved quick-task record-scoped-completion-validation: a Project record's
completion check must validate only its declared math closure (record
derivations plus derivations declared by related notes), named ``check-math``
selections must verify and update only the selected Math Derivations, and
full ``validate`` plus unscoped ``check-math`` must stay strict global audits.

Scenario to acceptance mapping:
- test_record_completion_ignores_unrelated_mathdoc_defects:
  unrelated invalid math must not block a record-local completion check.
- test_record_completion_blocks_*: declared missing, unpaired, noncurrent,
  and deprecated Math Derivations still block completion, including on the
  non-interface early-return path.
- test_record_completion_enforces_marker_coverage_and_containment:
  implementation marker coverage and source-root containment remain enforced.
- test_related_note_derivation_joins_record_scope: derivations declared
  through a related note join the validated dependency union.
- test_named_check_math_update_scopes_to_selected_math: named verification
  and --update ignore unrelated legacy math knowledge, preserve unselected
  math bytes, and actually refresh the selected verified results.
- test_named_check_math_read_detects_selected_source_drift: named read-only
  verification still fails on drift of the selected source.
- test_full_validate_and_unscoped_math_stay_strict: the global audits still
  reject the same unrelated defects the record-local check ignored.
"""

import hashlib
import platform
import re

import sympy

try:
    from tests.scoped_completion_support import ScopedProjectCase
except ImportError:  # direct test-directory execution
    from scoped_completion_support import ScopedProjectCase

PROJECT_ID = "scope-demo"
WORK_RECORD = PROJECT_ID + "/quick-task/fixture-task"
IMPLEMENTATION = "implementation/force_reference.py"


def derivative_results(power):
    """Return the canonical (srepr, latex) oracle for d/dx x**power."""
    x = sympy.Symbol("x")
    derivative = sympy.diff(x ** power, x)
    return sympy.srepr(derivative), sympy.latex(derivative)


def derivative_script(power):
    """Real SymPy derivative protocol emitting the version-1 JSON payload."""
    return (
        '"""Real SymPy derivative protocol for the Kosmic Math Derivation."""\n'
        "import argparse\n"
        "import json\n"
        "import platform\n"
        "\n"
        "import sympy\n"
        "\n"
        "\n"
        "def main() -> None:\n"
        "    parser = argparse.ArgumentParser()\n"
        '    parser.add_argument("--kosmic-json", action="store_true")\n'
        "    parser.parse_args()\n"
        '    x = sympy.Symbol("x")\n'
        f"    derivative = sympy.diff(x ** {power}, x)\n"
        "    payload = {\n"
        '        "schema_version": 1,\n'
        '        "python_version": platform.python_version(),\n'
        '        "sympy_version": sympy.__version__,\n'
        '        "results": [{\n'
        '            "name": "derivative",\n'
        '            "srepr": sympy.srepr(derivative),\n'
        '            "latex": sympy.latex(derivative),\n'
        "        }],\n"
        "    }\n"
        "    print(json.dumps(payload, sort_keys=True))\n"
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    main()\n"
    )


def implementation_source(slugs, marked=True):
    """Finite implementation source citing one canonical MathDoc marker per slug."""
    lines = [
        '"""Finite implementation consuming verified MathDoc results."""',
        "",
    ]
    for index, slug in enumerate(slugs):
        if marked:
            marker = f"<!-- MathDoc: {PROJECT_ID}/{slug}#derivative -->"
        else:
            marker = f"<!-- consumed by the viewer, entry {index} -->"
        lines.append(f"VIEWER_MARKER_{index} = {marker!r}")
    lines.extend(
        [
            "",
            "",
            "def render(latex: str) -> str:",
            '    return "$$\\n" + latex + "\\n$$"',
            "",
        ]
    )
    return "\n".join(lines)


class RecordScopedMathTest(ScopedProjectCase):
    """Real-CLI record math scoping on isolated temporary Project vaults."""

    def mathdocs(self):
        return self.project / "mathdocs"

    def mathdocs_snapshot(self):
        return {
            path.relative_to(self.mathdocs()).as_posix(): path.read_bytes()
            for path in sorted(self.mathdocs().rglob("*"))
            if path.is_file()
        }

    def run_expect(self, *arguments, expected):
        result = self.run_cli(*arguments)
        self.assertEqual(
            expected,
            result.returncode,
            msg=f"unexpected exit for {arguments[0]}:\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def run_completion(self, expected):
        return self.run_expect(
            "check-completion",
            "--project", self.project,
            "--work-item", self.project / "specs/quick-tasks/change.md",
            expected=expected,
        )

    def write_derivative_pair(self, slug, power):
        """Write one current, verified, indexed Math Derivation pair."""
        script = self.mathdocs() / f"{slug}.py"
        script_text = derivative_script(power)
        script.write_text(script_text, encoding="utf-8")
        srepr, latex = derivative_results(power)
        (self.mathdocs() / f"{slug}.md").write_text(
            "---\n"
            "type: Math Derivation\n"
            "status: stable\n"
            f"derivation: {slug}.py\n"
            f"source_sha256: {hashlib.sha256(script_text.encode()).hexdigest()}\n"
            f"python_version: {platform.python_version()}\n"
            f"sympy_version: {sympy.__version__}\n"
            "verified_at: 2026-09-05T12:00:00Z\n"
            "verified_host: test-host\n"
            f"verified_directory: {self.root.resolve()}\n"
            "---\n"
            "\n"
            f"# {slug.title()}\n"
            "\n"
            "<!-- KOSMIC-MATH-RESULTS:START -->\n"
            "## Verified Results\n"
            "\n"
            f"<!-- MathDoc: {PROJECT_ID}/{slug}#derivative -->\n"
            "$$\n"
            f"{latex}\n"
            "$$\n"
            f"<!-- KOSMIC-SREPR: {srepr} -->\n"
            "<!-- KOSMIC-MATH-RESULTS:END -->\n",
            encoding="utf-8",
        )
        with (self.mathdocs() / "index.md").open("a", encoding="utf-8") as handle:
            handle.write(f"| [{slug}]({slug}.md) | stable | {slug} derivative |\n")
        return script

    def write_deprecated_pair(self, slug):
        """Write an unindexed deprecated Math Derivation pair."""
        (self.mathdocs() / f"{slug}.py").write_text(
            derivative_script(2), encoding="utf-8"
        )
        (self.mathdocs() / f"{slug}.md").write_text(
            "---\n"
            "type: Math Derivation\n"
            "status: deprecated\n"
            f"derivation: {slug}.py\n"
            "---\n"
            "\n"
            f"# {slug.title()}\n"
            "\n"
            "Superseded derivation retained for history.\n",
            encoding="utf-8",
        )

    def write_stale_pair(self, slug, power):
        script = self.write_derivative_pair(slug, power)
        script.write_text(
            script.read_text(encoding="utf-8") + "\n# drifted after verification\n",
            encoding="utf-8",
        )
        return script

    def write_implementation(self, relative, slugs, marked=True):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(implementation_source(slugs, marked=marked), encoding="utf-8")
        return path

    def write_record(self, *, interface, derivations=None, files=None, related=None):
        lines = [
            f"consumer_interface_change: {'true' if interface else 'false'}",
        ]
        if derivations is not None:
            lines.append("derivations: [" + ", ".join(derivations) + "]")
        if files is not None:
            lines.append("math_implementation_files: [" + ", ".join(files) + "]")
        if related is not None:
            lines.append("related_notes: [" + ", ".join(related) + "]")
        return self.item("\n".join(lines) + "\n")

    def write_legacy_math_note(self):
        """A regular legacy knowledge note whose display math carries no marker."""
        self.note(
            "legacy_math.md",
            body="# Legacy math\n\n$$\n1\n$$\n",
        )

    def test_record_completion_ignores_unrelated_mathdoc_defects(self):
        self.write_derivative_pair("force", 2)
        self.write_implementation(IMPLEMENTATION, ["force"])
        self.write_record(
            interface=False,
            derivations=["force"],
            files=[IMPLEMENTATION],
        )
        # Unrelated defects only: an unpaired stray script, a stale pair, and
        # an unindexed deprecated pair.
        (self.mathdocs() / "ghost.py").write_text(
            derivative_script(2), encoding="utf-8"
        )
        self.write_stale_pair("legacy", 5)
        self.write_deprecated_pair("old")

        result = self.run_completion(0)
        self.assertIn("completion gate passed", result.stdout)

    def test_record_completion_blocks_malformed_selected_index_row(self):
        self.write_derivative_pair("force", 2)
        self.write_implementation(IMPLEMENTATION, ["force"])
        self.write_record(
            interface=False,
            derivations=["force"],
            files=[IMPLEMENTATION],
        )
        # Malformed extra rows naming the selected slug must not be silently
        # discarded by the scoped index filter: link syntax and bare slug.
        malformed_rows = (
            "| [force](force.md) | invalid | duplicate |\n",
            "| [force](force.md | stable | duplicate |\n",
            "| force | stable | duplicate |\n",
        )
        for row in malformed_rows:
            with self.subTest(row=row):
                index = self.mathdocs() / "index.md"
                original = index.read_text(encoding="utf-8")
                index.write_text(original + row, encoding="utf-8")
                result = self.run_completion(2)
                self.assertIn("invalid mathdocs index row", result.stderr)
                index.write_text(original, encoding="utf-8")

    def test_record_completion_ignores_unrelated_malformed_index_row(self):
        self.write_derivative_pair("force", 2)
        self.write_implementation(IMPLEMENTATION, ["force"])
        self.write_record(
            interface=False,
            derivations=["force"],
            files=[IMPLEMENTATION],
        )
        # Malformed unrelated rows are skipped even when a later column
        # happens to mention the selected slug.
        with (self.mathdocs() / "index.md").open("a", encoding="utf-8") as handle:
            handle.write(
                "| [legacy](legacy.md) | broken | mentions force.md |\n"
                "| legacy | broken | extra | column |\n"
            )

        result = self.run_completion(0)
        self.assertIn("completion gate passed", result.stdout)

    def test_record_completion_blocks_missing_selected_derivation(self):
        self.write_derivative_pair("force", 2)
        self.write_implementation(IMPLEMENTATION, ["force"])
        self.write_record(
            interface=False,
            derivations=["absent"],
            files=[IMPLEMENTATION],
        )

        result = self.run_completion(2)
        self.assertIn("selected MathDoc is missing: absent", result.stderr)

    def test_record_completion_blocks_unpaired_selected_derivation(self):
        self.write_derivative_pair("force", 2)
        (self.mathdocs() / "ghost.py").write_text(
            derivative_script(2), encoding="utf-8"
        )
        self.write_implementation(IMPLEMENTATION, ["ghost"])
        self.write_record(
            interface=False,
            derivations=["ghost"],
            files=[IMPLEMENTATION],
        )

        result = self.run_completion(2)
        self.assertIn("unpaired mathdocs files: ghost.py", result.stderr)

    def test_record_completion_blocks_noncurrent_selected_source(self):
        script = self.write_derivative_pair("force", 2)
        self.write_implementation(IMPLEMENTATION, ["force"])
        self.write_record(
            interface=False,
            derivations=["force"],
            files=[IMPLEMENTATION],
        )
        script.write_text(derivative_script(3), encoding="utf-8")

        result = self.run_completion(2)
        self.assertIn(
            "Math Derivation force source_sha256 does not match force.py",
            result.stderr,
        )

    def test_record_completion_blocks_deprecated_selected_derivation(self):
        self.write_derivative_pair("force", 2)
        self.write_deprecated_pair("old")
        self.write_implementation(IMPLEMENTATION, ["old"])
        self.write_record(
            interface=False,
            derivations=["old"],
            files=[IMPLEMENTATION],
        )

        result = self.run_completion(2)
        self.assertIn(
            "work-item derivation is not stable and current: old",
            result.stderr,
        )

    def test_record_completion_enforces_marker_coverage_and_containment(self):
        self.write_derivative_pair("force", 2)
        self.write_derivative_pair("alloy", 3)

        self.write_implementation(IMPLEMENTATION, ["force"], marked=False)
        self.write_record(
            interface=False,
            derivations=["force"],
            files=[IMPLEMENTATION],
        )
        unmarked = self.run_completion(2)
        self.assertIn(
            "math implementation file has no declared MathDoc reference: "
            + IMPLEMENTATION,
            unmarked.stderr,
        )

        self.write_implementation(IMPLEMENTATION, ["force"])
        self.write_record(
            interface=False,
            derivations=["force", "alloy"],
            files=[IMPLEMENTATION],
        )
        uncovered = self.run_completion(2)
        self.assertIn(
            "declared derivations have no implementation reference: alloy",
            uncovered.stderr,
        )

        self.write_record(
            interface=False,
            derivations=["force"],
            files=["../force_reference.py"],
        )
        escaping = self.run_completion(2)
        self.assertIn(
            "math implementation path must be relative and non-traversing: "
            "../force_reference.py",
            escaping.stderr,
        )

    def test_related_note_derivation_joins_record_scope(self):
        script = self.write_derivative_pair("force", 2)
        _, latex = derivative_results(2)
        self.note(
            "math-usage.md",
            body=(
                "# Math usage\n"
                "\n"
                "The viewer renders the verified force derivative:\n"
                "\n"
                f"<!-- MathDoc: {PROJECT_ID}/force#derivative -->\n"
                "$$\n"
                f"{latex}\n"
                "$$\n"
            ),
            metadata="derivations: [mathdocs/force.py]\n",
        )
        self.run_expect(
            "generate", "--project", self.project, "--work-record", WORK_RECORD,
            expected=0,
        )
        self.write_record(interface=True, related=["math-usage"])
        # Unrelated stale pair only; the record declares no derivations of
        # its own, so force reaches the closure through the related note.
        self.write_stale_pair("legacy", 5)

        self.run_completion(0)

        original = script.read_bytes()
        script.write_text(derivative_script(3), encoding="utf-8")
        drifted = self.run_completion(2)
        self.assertIn(
            "Math Derivation force source_sha256 does not match force.py",
            drifted.stderr,
        )

        script.write_bytes(original)
        self.run_completion(0)

    def test_named_check_math_update_scopes_to_selected_math(self):
        script = self.write_derivative_pair("force", 2)
        self.write_legacy_math_note()
        self.write_stale_pair("legacy", 5)

        selected = self.run_expect(
            "check-math", "--project", self.project, "--slug", "force",
            expected=0,
        )
        self.assertIn("force: PASS", selected.stdout)
        self.assertNotIn("legacy", selected.stdout)
        self.assertNotIn("legacy", selected.stderr)

        stale_srepr, _ = derivative_results(2)
        fresh_srepr, fresh_latex = derivative_results(3)
        stale_digest = hashlib.sha256(script.read_bytes()).hexdigest()
        script.write_text(derivative_script(3), encoding="utf-8")
        fresh_digest = hashlib.sha256(script.read_bytes()).hexdigest()
        before = self.mathdocs_snapshot()

        updated = self.run_expect(
            "check-math", "--project", self.project, "--slug", "force",
            "--update", "--work-record", WORK_RECORD,
            expected=0,
        )
        self.assertIn("force: PASS", updated.stdout)
        note = (self.mathdocs() / "force.md").read_text(encoding="utf-8")
        self.assertIn(f"source_sha256: {fresh_digest}", note)
        self.assertNotIn(stale_digest, note)
        self.assertIn(f"<!-- KOSMIC-SREPR: {fresh_srepr} -->", note)
        self.assertNotIn(stale_srepr, note)
        self.assertIn(fresh_latex, note)

        after = self.mathdocs_snapshot()
        self.assertEqual(sorted(before), sorted(after))
        for name, data in before.items():
            if name != "force.md":
                self.assertEqual(data, after[name], f"unselected {name} changed")

        self.run_expect(
            "check-math", "--project", self.project, "--slug", "force",
            expected=0,
        )

        self.run_expect("validate", "--project", self.project, expected=2)
        self.assertIn(
            "Math Derivation legacy source_sha256 does not match legacy.py",
            self.run_expect("check-math", "--project", self.project, expected=2).stderr,
        )

    def test_named_check_math_read_detects_selected_source_drift(self):
        script = self.write_derivative_pair("force", 2)
        self.write_legacy_math_note()

        self.run_expect(
            "check-math", "--project", self.project, "--slug", "force",
            expected=0,
        )

        script.write_text(derivative_script(4), encoding="utf-8")
        drifted = self.run_expect(
            "check-math", "--project", self.project, "--slug", "force",
            expected=2,
        )
        self.assertIn(
            "Math Derivation force source_sha256 does not match force.py",
            drifted.stderr,
        )
        self.assertNotIn("legacy", drifted.stderr)

    def test_full_validate_and_unscoped_math_stay_strict(self):
        self.write_derivative_pair("force", 2)
        self.note("using.md")
        self.run_expect(
            "generate", "--project", self.project, "--work-record", WORK_RECORD,
            expected=0,
        )
        legacy_script = self.write_stale_pair("legacy", 5)
        (self.mathdocs() / "ghost.py").write_text(
            derivative_script(2), encoding="utf-8"
        )
        self.write_legacy_math_note()

        unpaired = self.run_expect("validate", "--project", self.project, expected=2)
        self.assertIn("unpaired mathdocs files: ghost.py", unpaired.stderr)
        self.assertIn(
            "unpaired mathdocs files: ghost.py",
            self.run_expect("check-math", "--project", self.project, expected=2).stderr,
        )

        (self.mathdocs() / "ghost.py").unlink()
        stale = self.run_expect("validate", "--project", self.project, expected=2)
        self.assertIn(
            "Math Derivation legacy source_sha256 does not match legacy.py",
            stale.stderr,
        )
        self.assertIn(
            "Math Derivation legacy source_sha256 does not match legacy.py",
            self.run_expect("check-math", "--project", self.project, expected=2).stderr,
        )

        legacy_note = self.mathdocs() / "legacy.md"
        legacy_note.write_text(
            re.sub(
                r"source_sha256: [0-9a-f]{64}",
                "source_sha256: "
                + hashlib.sha256(legacy_script.read_bytes()).hexdigest(),
                legacy_note.read_text(encoding="utf-8"),
            ),
            encoding="utf-8",
        )
        broken_note = self.run_expect(
            "validate", "--project", self.project, expected=2
        )
        self.assertIn("legacy_math.md", broken_note.stderr)
        self.assertIn(
            "legacy_math.md",
            self.run_expect("check-math", "--project", self.project, expected=2).stderr,
        )
