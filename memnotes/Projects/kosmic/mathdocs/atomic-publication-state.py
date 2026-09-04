#!/usr/bin/env python3
"""Executable MathDoc for atomic Project Skill Pair publication."""

from __future__ import annotations

import argparse
import json
import platform
import sympy


def derive() -> dict[str, sympy.Expr]:
    """Reduce publication outcomes modulo the binary success constraint."""
    success = sympy.symbols("s", integer=True)
    binary_constraint = success**2 - success
    new_visible = success
    old_visible = 1 - success
    return {
        "commit_indicator": new_visible,
        "mixed_visibility": sympy.rem(
            new_visible * old_visible, binary_constraint, success
        ),
        "rollback_indicator": old_visible,
        "visible_count": sympy.rem(
            new_visible + old_visible, binary_constraint, success
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kosmic-json", action="store_true")
    args = parser.parse_args()
    results = derive()
    payload = {
        "schema_version": 1,
        "python_version": platform.python_version(),
        "sympy_version": sympy.__version__,
        "results": [
            {"name": name, "srepr": sympy.srepr(expr), "latex": sympy.latex(expr)}
            for name, expr in sorted(results.items())
        ],
    }
    if args.kosmic_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        for result in payload["results"]:
            print(f"{result['name']}: {result['latex']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
