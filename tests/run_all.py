"""Run tests in fresh per-module interpreters with finite module and suite limits.

Usage: python tests/run_all.py [pattern ...]
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
RUNNER_TIMEOUT_SECONDS = 600
MODULE_TIMEOUT_SECONDS = 240


def main() -> int:
    patterns = sys.argv[1:]
    modules = sorted(
        path.stem for path in TESTS_DIR.glob("test_*.py")
        if not patterns or any(pattern in path.stem for pattern in patterns)
    )
    if not modules:
        print("no test modules matched", file=sys.stderr)
        return 2
    failures: list[str] = []
    started = time.monotonic()
    deadline = started + RUNNER_TIMEOUT_SECONDS
    for module in modules:
        module_start = time.monotonic()
        remaining = min(MODULE_TIMEOUT_SECONDS, deadline - time.monotonic())
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "unittest", f"tests.{module}", "-q"],
                cwd=REPO_ROOT, capture_output=True, text=True,
                timeout=max(0.1, remaining),
            )
            status = "ok" if completed.returncode == 0 else "FAILED"
            if completed.returncode != 0:
                failures.append(module)
                print(completed.stderr, end="", file=sys.stderr)
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
            failures.append(module)
            print(f"{module}: exceeded remaining runner/module deadline", file=sys.stderr)
        print(f"{status:7s} {module:40s} {time.monotonic() - module_start:6.2f}s",
              flush=True)
    elapsed = time.monotonic() - started
    print(f"\n{len(modules)} modules in {elapsed:.1f}s; "
          f"{len(failures)} failed: {', '.join(failures) or 'none'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
