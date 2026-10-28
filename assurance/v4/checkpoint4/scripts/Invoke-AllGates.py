#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CP4 = ROOT / "checkpoint4-v4"
REPORTS = CP4 / "reports"
FIXTURE = ROOT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
SAMPLE = REPORTS / "reviewed-lab-evaluation.json"


def run(label: str, command: list[str]) -> tuple[bool, str]:
    print(f"> [{label}] " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=ROOT, text=True)
    return result.returncode == 0, label


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    steps = [
        ("checkpoint3-gates", [sys.executable, "checkpoint3-v4/scripts/Invoke-AllGates.py"]),
        ("legacy-assets", [sys.executable, "tools/Sync-ReportAssets.py", "--check"]),
        ("legacy-criteria", [sys.executable, "tools/Test-CriteriaCoverage.py"]),
        ("legacy-report-contract", [sys.executable, "tools/Test-ReportContract.py"]),
        ("legacy-lab-contract", [sys.executable, "tools/Test-LabCorrections.py"]),
        ("generate-sample", [sys.executable, "checkpoint4-v4/scripts/Evaluate-Posture.py", "--evidence", str(FIXTURE), "--output", str(SAMPLE)]),
        ("cp4-json-schemas", [sys.executable, "checkpoint4-v4/validators/Validate-JsonSchemas.py"]),
        ("cp4-engine-contracts", [sys.executable, "checkpoint4-v4/validators/Validate-EngineContracts.py"]),
        ("cp4-traceability", [sys.executable, "checkpoint4-v4/validators/Validate-Traceability.py"]),
        ("cp4-priority-roadmap", [sys.executable, "checkpoint4-v4/validators/Validate-PriorityRoadmap.py"]),
        ("false-positive-tests", [sys.executable, "checkpoint4-v4/tests/Test-FalsePositiveGuards.py"]),
        ("determinism-tests", [sys.executable, "checkpoint4-v4/tests/Test-Determinism.py"]),
        ("priority-tests", [sys.executable, "checkpoint4-v4/tests/Test-Priority.py"]),
        ("before-after-tests", [sys.executable, "checkpoint4-v4/tests/Test-BeforeAfter.py"]),
        ("python-compile", [sys.executable, "-m", "compileall", "-q", "checkpoint4-v4"]),
    ]
    failures = []
    for label, command in steps:
        ok, name = run(label, command)
        if not ok:
            failures.append(name)
    parse_errors = []
    for path in sorted((CP4 / "schemas").glob("*.json")) + [CP4 / "manifest.json", SAMPLE]:
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            parse_errors.append(f"{path.relative_to(ROOT)}: {exc}")
    if parse_errors:
        failures.extend(parse_errors)
        print("[FAIL] JSON parse gate")
        for error in parse_errors: print(" - " + error)
    else:
        print("[PASS] JSON parse gate")
    status = {
        "checkpoint": 4,
        "version": "4.0.0",
        "engineVersion": "4.0.0-checkpoint4",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }
    (REPORTS / "last-gate-result.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    if failures:
        print("[FAIL] CHECKPOINT 4 V4 - " + ", ".join(failures))
        return 1
    print("[PASS] CHECKPOINT 4 V4 - ALL GATES PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
