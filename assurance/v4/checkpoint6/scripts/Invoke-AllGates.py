#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CP5 = ROOT / "assurance/v4/checkpoint5"
CP6 = ROOT / "assurance/v4/checkpoint6"
REPORTS = CP6 / "reports"
ARTIFACTS = REPORTS / "validation"
FIXTURE = ROOT / "tests/fixtures/reviewed-lab-sanitized.zip"
ASSESSMENT = REPORTS / "assessment-result.v4.json"
EN = REPORTS / "arc-posture-review.v4.en-US.html"
PT = REPORTS / "arc-posture-review.v4.pt-BR.html"


def run(label: str, command: list[str]) -> bool:
    print(f"> [{label}] " + " ".join(map(str, command)), flush=True)
    return subprocess.run(command, cwd=ROOT, text=True).returncode == 0


def main() -> int:
    if REPORTS.exists():
        shutil.rmtree(REPORTS)
    REPORTS.mkdir(parents=True)
    cli = CP5 / "cli/arc_posture.py"
    renderer = CP6 / "report/render_v4.py"
    tests = CP6 / "tests"
    steps = [
        ("cp6-generate-canonical-no-baseline", [sys.executable, str(cli), "evaluate", "--evidence", str(FIXTURE), "--output", str(ASSESSMENT)]),
        ("cp6-render-en-US", [sys.executable, str(renderer), "--input", str(ASSESSMENT), "--output", str(EN), "--locale", "en-US"]),
        ("cp6-render-pt-BR", [sys.executable, str(renderer), "--input", str(ASSESSMENT), "--output", str(PT), "--locale", "pt-BR"]),
        ("cp6-render-purity", [sys.executable, str(tests / "Test-RenderPurity.py")]),
        ("cp6-validation-notice", [sys.executable, str(tests / "Test-ValidationNotice.py")]),
        ("cp6-contract-en-US", [sys.executable, str(tests / "Test-ReportContract.py"), "--assessment", str(ASSESSMENT), "--html", str(EN)]),
        ("cp6-contract-pt-BR", [sys.executable, str(tests / "Test-ReportContract.py"), "--assessment", str(ASSESSMENT), "--html", str(PT)]),
        ("cp6-localization-parity", [sys.executable, str(tests / "Test-LocalizationParity.py"), "--en", str(EN), "--pt", str(PT)]),
        ("cp6-playwright-and-pdf", [sys.executable, str(tests / "Test-ReportVisual.py"), "--en", str(EN), "--pt", str(PT), "--artifacts", str(ARTIFACTS)]),
        ("cp6-python-compile", [sys.executable, "-m", "compileall", "-q", str(CP6)]),
    ]
    failures = [label for label, command in steps if not run(label, command)]
    status = {"checkpoint": 6, "version": "4.2.0", "contract": "assessment-result.v4", "renderMode": "render-only", "status": "FAIL" if failures else "PASS", "failures": failures}
    (REPORTS / "last-gate-result.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    if failures:
        print("[FAIL] CHECKPOINT 6 - " + ", ".join(failures))
        return 1
    print("[PASS] CHECKPOINT 6 - CANONICAL RENDERER, BILINGUAL PLAYWRIGHT AND PDF GATES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
