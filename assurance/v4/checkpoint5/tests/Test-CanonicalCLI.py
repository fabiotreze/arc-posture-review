#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from test_lib import CP5, FIXTURE


def run(*args):
    return subprocess.run([sys.executable, str(CP5 / "cli" / "arc_posture.py"), *map(str, args)], text=True, capture_output=True)


def main() -> int:
    errors = []
    with tempfile.TemporaryDirectory(prefix="arc-posture-cp5-") as temp:
        folder = Path(temp); before = folder / "before.json"; after = folder / "after.json"; comparison = folder / "comparison.json"
        first = run("evaluate", "--evidence", FIXTURE, "--output", before)
        second = run("evaluate", "--evidence", FIXTURE, "--baseline", FIXTURE, "--output", after)
        third = run("compare", "--before", before, "--after", after, "--output", comparison)
        for label, process in (("evaluate", first), ("evaluate-baseline", second), ("compare", third)):
            if process.returncode: errors.append(f"{label}: {process.stderr or process.stdout}")
        if not errors:
            current = json.loads(after.read_text(encoding="utf-8")); delta = json.loads(comparison.read_text(encoding="utf-8"))
            if current["metadata"]["contractName"] != "assessment-result.v4": errors.append("CLI assessment contract")
            if current["comparison"]["summary"] != {"IMPROVED": 0, "REGRESSED": 0, "UNCHANGED": 64}: errors.append("CLI embedded comparison")
            if delta["contractName"] != "assessment-comparison.v4" or len(delta["controls"]) != 64: errors.append("CLI comparison contract")
    if errors:
        print(f"[FAIL] canonical CLI: {len(errors)} error(s)")
        for error in errors: print(" - " + error)
        return 1
    print("[PASS] canonical CLI: evaluate and compare")
    return 0


if __name__ == "__main__": raise SystemExit(main())
