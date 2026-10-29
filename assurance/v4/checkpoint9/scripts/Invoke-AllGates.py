#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CP9 = ROOT / "assurance/v4/checkpoint9"


def main() -> int:
    commands = [
        [sys.executable, str(CP9 / "tests/Test-SecurityReviewPackage.py")],
        [sys.executable, "-m", "compileall", "-q", str(CP9)],
    ]
    failures = []
    for command in commands:
        print("> [cp9] " + " ".join(command), flush=True)
        if subprocess.run(command, cwd=ROOT, text=True).returncode: failures.append(" ".join(command))
    if failures: print("[FAIL] CHECKPOINT 9"); return 1
    print("[PASS] CHECKPOINT 9 - v4.0.0-rc.1 SECURITY REVIEW PACKAGE")
    return 0


if __name__ == "__main__": raise SystemExit(main())
