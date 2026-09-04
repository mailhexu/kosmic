#!/usr/bin/env python3
"""Executable SymPy derivation for one Kosmic MathDoc."""

from __future__ import annotations

import argparse
import json
import platform

import sympy


def derive() -> list[dict[str, str]]:
    """Return named results in lexical order."""
    # Define symbols with explicit assumptions, derive results, then replace this example.
    x = sympy.symbols("x", real=True)
    expression = sympy.simplify(x)
    return [
        {
            "name": "result_name",
            "srepr": sympy.srepr(expression),
            "latex": sympy.latex(expression),
        }
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kosmic-json", action="store_true")
    args = parser.parse_args()
    if not args.kosmic_json:
        parser.error("this derivation is machine-driven; pass --kosmic-json")
    payload = {
        "schema_version": 1,
        "python_version": platform.python_version(),
        "sympy_version": sympy.__version__,
        "results": derive(),
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
