#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CP4_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CP4_ROOT))

from engine.repository_layout import (
    REPO_ROOT,
    CP3_ROOT,
    CP4_ROOT,
    CP4_REPORTS,
    REVIEWED_LAB_FIXTURE,
    REVIEWED_LAB_REPORT,
    validate_layout,
)


def run(label: str, command: list[str], cwd: Path | None = None) -> bool:
    print(
        f"> [{label}] " + " ".join(str(x) for x in command),
        flush=True,
    )

    result = subprocess.run(
        command,
        cwd=str(cwd or REPO_ROOT),
        text=True,
    )

    return result.returncode == 0


def main() -> int:
    failures: list[str] = []

    try:
        validate_layout()
        print("[PASS] integrated repository layout")
    except Exception as exc:
        print(f"[FAIL] integrated repository layout: {exc}")
        return 1

    CP4_REPORTS.mkdir(parents=True, exist_ok=True)

    py = sys.executable

    steps = [
        (
            "cp1-schema",
            [py, str(REPO_ROOT / "tools" / "Test-V4Schema.py")],
        ),
        (
            "cp1-taxonomy",
            [py, str(REPO_ROOT / "tools" / "Test-V4Taxonomy.py")],
        ),
        (
            "cp2-mapping",
            [py, str(REPO_ROOT / "tools" / "Test-V4Mapping.py")],
        ),
        (
            "cp3-json-schemas",
            [
                py,
                str(
                    CP3_ROOT
                    / "validators"
                    / "Validate-JsonSchemas.py"
                ),
            ],
        ),
        (
            "cp3-mappings",
            [
                py,
                str(
                    CP3_ROOT
                    / "validators"
                    / "Validate-Mappings.py"
                ),
            ],
        ),
        (
            "cp3-claims",
            [
                py,
                str(
                    CP3_ROOT
                    / "validators"
                    / "Validate-Claims.py"
                ),
            ],
        ),
        (
            "cp3-scenarios",
            [
                py,
                str(
                    CP3_ROOT
                    / "validators"
                    / "Validate-SecurityScenarios.py"
                ),
            ],
        ),
        (
            "cp3-attack-path-negative",
            [
                py,
                str(
                    CP3_ROOT
                    / "tests"
                    / "Test-AttackPathHypotheses.py"
                ),
            ],
        ),
        (
            "legacy-assets",
            [
                py,
                str(REPO_ROOT / "tools" / "Sync-ReportAssets.py"),
                "--check",
            ],
        ),
        (
            "legacy-criteria",
            [
                py,
                str(REPO_ROOT / "tools" / "Test-CriteriaCoverage.py"),
            ],
        ),
        (
            "legacy-report-contract",
            [
                py,
                str(REPO_ROOT / "tools" / "Test-ReportContract.py"),
            ],
        ),
        (
            "legacy-lab-contract",
            [
                py,
                str(REPO_ROOT / "tools" / "Test-LabCorrections.py"),
            ],
        ),
        (
            "generate-sample",
            [
                py,
                str(CP4_ROOT / "scripts" / "Evaluate-Posture.py"),
                "--evidence",
                str(REVIEWED_LAB_FIXTURE),
                "--output",
                str(REVIEWED_LAB_REPORT),
            ],
        ),
        (
            "cp4-json-schemas",
            [
                py,
                str(
                    CP4_ROOT
                    / "validators"
                    / "Validate-JsonSchemas.py"
                ),
            ],
        ),
        (
            "cp4-engine-contracts",
            [
                py,
                str(
                    CP4_ROOT
                    / "validators"
                    / "Validate-EngineContracts.py"
                ),
            ],
        ),
        (
            "cp4-traceability",
            [
                py,
                str(
                    CP4_ROOT
                    / "validators"
                    / "Validate-Traceability.py"
                ),
            ],
        ),
        (
            "cp4-priority-roadmap",
            [
                py,
                str(
                    CP4_ROOT
                    / "validators"
                    / "Validate-PriorityRoadmap.py"
                ),
            ],
        ),
        (
            "false-positive-tests",
            [
                py,
                str(
                    CP4_ROOT
                    / "tests"
                    / "Test-FalsePositiveGuards.py"
                ),
            ],
        ),
        (
            "determinism-tests",
            [
                py,
                str(
                    CP4_ROOT
                    / "tests"
                    / "Test-Determinism.py"
                ),
            ],
        ),
        (
            "priority-tests",
            [
                py,
                str(
                    CP4_ROOT
                    / "tests"
                    / "Test-Priority.py"
                ),
            ],
        ),
        (
            "before-after-tests",
            [
                py,
                str(
                    CP4_ROOT
                    / "tests"
                    / "Test-BeforeAfter.py"
                ),
            ],
        ),
        (
            "python-compile",
            [
                py,
                "-m",
                "compileall",
                "-q",
                str(CP4_ROOT),
            ],
        ),
    ]

    for label, command in steps:
        if not run(label, command):
            failures.append(label)

    parse_errors: list[str] = []

    paths = (
        sorted((CP4_ROOT / "schemas").glob("*.json"))
        + [CP4_ROOT / "manifest.json"]
    )

    if REVIEWED_LAB_REPORT.exists():
        paths.append(REVIEWED_LAB_REPORT)
    else:
        parse_errors.append(
            "reviewed-lab-evaluation.json was not generated"
        )

    for path in paths:
        try:
            json.loads(
                path.read_text(encoding="utf-8-sig")
            )
        except Exception as exc:
            parse_errors.append(
                f"{path}: {exc}"
            )

    if parse_errors:
        failures.append("json-parse")
        print("[FAIL] JSON parse gate")

        for error in parse_errors:
            print(" - " + error)
    else:
        print("[PASS] JSON parse gate")

    if failures:
        print(
            "[FAIL] CHECKPOINT 4.1 V4 - "
            + ", ".join(failures)
        )
        return 1

    print(
        "[PASS] CHECKPOINT 4.1 V4 - "
        "ALL INTEGRATED GATES PASSED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
