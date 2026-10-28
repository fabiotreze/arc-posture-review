#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
CP5 = REPO_ROOT / "assurance" / "v4" / "checkpoint5"
REPORTS = CP5 / "reports"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
ASSESSMENT = REPORTS / "assessment-result.v4.json"
COMPARISON = REPORTS / "assessment-comparison.v4.json"


def run(label: str, command: list[str]) -> bool:
    print(f"> [{label}] " + " ".join(map(str, command)), flush=True)
    result = subprocess.run(command, cwd=REPO_ROOT, text=True)
    return result.returncode == 0


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    cli = CP5 / "cli" / "arc_posture.py"
    steps = [
        ("generate-canonical-assessment", [sys.executable, str(cli), "evaluate", "--evidence", str(FIXTURE), "--baseline", str(FIXTURE), "--output", str(ASSESSMENT)]),
        ("generate-canonical-comparison", [sys.executable, str(cli), "compare", "--before", str(ASSESSMENT), "--after", str(ASSESSMENT), "--output", str(COMPARISON)]),
        ("cp5-json-schemas", [sys.executable, str(CP5 / "validators" / "Validate-JsonSchemas.py")]),
        ("cp5-semantic-contract", [sys.executable, str(CP5 / "validators" / "Validate-CanonicalSemantic.py")]),
        ("cp5-contract-tests", [sys.executable, str(CP5 / "tests" / "Test-CanonicalContract.py")]),
        ("cp5-determinism-tests", [sys.executable, str(CP5 / "tests" / "Test-CanonicalDeterminism.py")]),
        ("cp5-before-after-tests", [sys.executable, str(CP5 / "tests" / "Test-CanonicalCompare.py")]),
        ("cp5-cli-tests", [sys.executable, str(CP5 / "tests" / "Test-CanonicalCLI.py")]),
        ("cp5-python-compile", [sys.executable, "-m", "compileall", "-q", str(CP5)]),
    ]
    failures = [label for label, command in steps if not run(label, command)]
    status = {
        "checkpoint": 5,
        "version": "4.1.0",
        "contract": "assessment-result.v4",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }
    (REPORTS / "last-gate-result.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    if failures:
        print("[FAIL] CHECKPOINT 5 - " + ", ".join(failures))
        return 1
    print("[PASS] CHECKPOINT 5 - ALL GATES PASSED")
    return 0


if __name__ == "__main__": raise SystemExit(main())
