#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CP6 = ROOT / "assurance/v4/checkpoint6"
CP7 = ROOT / "assurance/v4/checkpoint7"
REPORTS = CP7 / "reports"
ASSESSMENT = REPORTS / "assessment-with-comparison.v4.json"
HTML = REPORTS / "arc-posture-review.before-after.en-US.html"


def run(label: str, command: list[str]) -> bool:
    print(f"> [{label}] " + " ".join(map(str, command)), flush=True)
    return subprocess.run(command, cwd=ROOT, text=True).returncode == 0


def main() -> int:
    if REPORTS.exists(): shutil.rmtree(REPORTS)
    REPORTS.mkdir(parents=True)
    steps = [
        ("cp7-canonical-before-after", [sys.executable, str(CP7 / "tests/Test-BeforeAfterReport.py"), "--output", str(ASSESSMENT)]),
        ("cp7-render-comparison", [sys.executable, str(CP6 / "report/render_v4.py"), "--input", str(ASSESSMENT), "--output", str(HTML), "--locale", "en-US"]),
        ("cp7-report-contract", [sys.executable, str(CP6 / "tests/Test-ReportContract.py"), "--assessment", str(ASSESSMENT), "--html", str(HTML)]),
        ("cp7-visual", [sys.executable, str(CP7 / "tests/Test-ComparisonVisual.py"), "--html", str(HTML), "--screenshot", str(REPORTS / "verified-improvement.png")]),
        ("cp7-python-compile", [sys.executable, "-m", "compileall", "-q", str(CP7)]),
    ]
    failures = [label for label, command in steps if not run(label, command)]
    if failures:
        print("[FAIL] CHECKPOINT 7 - " + ", ".join(failures))
        return 1
    print("[PASS] CHECKPOINT 7 - BEFORE/AFTER, VERIFIED IMPROVEMENT AND NULL-COMPARISON COMPATIBILITY")
    return 0


if __name__ == "__main__": raise SystemExit(main())
