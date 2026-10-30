#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CP10 = ROOT / "assurance/v4/checkpoint10"


def main() -> int:
    commands = [
        [sys.executable, str(CP10 / "tests/Test-ReleasePreparation.py")],
        [sys.executable, "-m", "compileall", "-q", str(CP10)],
    ]
    failures = []
    for command in commands:
        print("> [cp10] " + " ".join(command), flush=True)
        if subprocess.run(command, cwd=ROOT, text=True).returncode: failures.append(" ".join(command))
    if failures: print("[FAIL] CHECKPOINT 10"); return 1
    manifest = json.loads((CP10 / "manifest.json").read_text(encoding="utf-8"))
    print(f"[PASS] CHECKPOINT 10 - {manifest.get('release')} RELEASE PREPARATION ({manifest.get('status')})")
    return 0


if __name__ == "__main__": raise SystemExit(main())
