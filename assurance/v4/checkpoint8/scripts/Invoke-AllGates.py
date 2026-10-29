#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CP8 = ROOT / "assurance/v4/checkpoint8"


def main() -> int:
    steps = [
        ("cp8-workflows", [sys.executable, str(CP8 / "tests/Test-DevSecOpsWorkflows.py")]),
        ("cp8-python-compile", [sys.executable, "-m", "compileall", "-q", str(CP8)]),
    ]
    failures = []
    for label, command in steps:
        print(f"> [{label}] " + " ".join(command), flush=True)
        if subprocess.run(command, cwd=ROOT, text=True).returncode: failures.append(label)
    if failures:
        print("[FAIL] CHECKPOINT 8 - " + ", ".join(failures)); return 1
    print("[PASS] CHECKPOINT 8 - DEVSECOPS WORKFLOWS AND GATES")
    return 0


if __name__ == "__main__": raise SystemExit(main())
