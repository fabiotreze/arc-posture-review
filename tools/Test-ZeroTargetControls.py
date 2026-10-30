#!/usr/bin/env python3
"""Regression gate for Azure Arc scopes containing zero machines.

The collector must not produce PASS for machine-dependent controls when the
evaluated scope contains no microsoft.hybridcompute/machines resources.

This test intentionally fails until the v4.0.2 collector guard is implemented.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / "scripts" / "Invoke-ArcPostureReview.ps1"

MACHINE_DEPENDENT_CHECKS = (
    "CHK-12",
    "CHK-21",
    "CHK-23",
    "CHK-24",
    "CHK-27",
    "CHK-28",
    "CHK-32",
    "CHK-37",
    "CHK-39",
    "CHK-51",
)

REQUIRED_MARKERS = (
    "ZERO_TARGET_MACHINE_CHECKS",
    "No Azure Arc-enabled machine exists in the evaluated scope",
    "must not be interpreted as PASS",
)


def extract_eval_block(source: str, check_id: str) -> str:
    start_pattern = re.compile(
        rf"(?m)^\s*\$Eval\[['\"]{re.escape(check_id)}['\"]\]\s*=\s*\{{"
    )
    match = start_pattern.search(source)

    if not match:
        raise AssertionError(f"{check_id}: Eval block not found")

    start = match.start()
    next_block = re.search(
        r"(?m)^\s*\$Eval\[['\"]CHK-\d{2}['\"]\]\s*=\s*\{",
        source[match.end():],
    )

    if next_block:
        end = match.end() + next_block.start()
    else:
        end = len(source)

    return source[start:end]


def main() -> int:
    if not COLLECTOR.exists():
        print(f"[FAIL] Collector not found: {COLLECTOR}")
        return 1

    source = COLLECTOR.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    errors: list[str] = []

    for check_id in MACHINE_DEPENDENT_CHECKS:
        try:
            extract_eval_block(source, check_id)
        except AssertionError as exc:
            errors.append(str(exc))

    for marker in REQUIRED_MARKERS:
        if marker not in source:
            errors.append(f"collector guard marker missing: {marker!r}")

    guard_set_pattern = re.compile(
        r"ZERO_TARGET_MACHINE_CHECKS"
        r".*?"
        r"CHK-12"
        r".*?"
        r"CHK-21"
        r".*?"
        r"CHK-23"
        r".*?"
        r"CHK-24"
        r".*?"
        r"CHK-27"
        r".*?"
        r"CHK-28"
        r".*?"
        r"CHK-32"
        r".*?"
        r"CHK-37"
        r".*?"
        r"CHK-39"
        r".*?"
        r"CHK-51",
        re.DOTALL,
    )

    if not guard_set_pattern.search(source):
        errors.append(
            "zero-target guard does not enumerate the expected "
            "machine-dependent controls"
        )

    zero_machine_pattern = re.compile(
        r"\$DS\[['\"]machines['\"]\]"
        r".*?"
        r"\.Count"
        r".*?"
        r"(?:-eq\s+0|-le\s+0|-not)",
        re.DOTALL | re.IGNORECASE,
    )

    if not zero_machine_pattern.search(source):
        errors.append(
            "collector does not explicitly test for zero Arc machines"
        )

    info_pattern = re.compile(
        r"Write-Result\s+['\"]INFO['\"]",
        re.IGNORECASE,
    )

    if not info_pattern.search(source):
        errors.append(
            "zero-target implementation does not emit INFO"
        )

    pass_override_pattern = re.compile(
        r"ZERO_TARGET_MACHINE_CHECKS"
        r".*?"
        r"Write-Result\s+['\"]INFO['\"]",
        re.DOTALL | re.IGNORECASE,
    )

    if not pass_override_pattern.search(source):
        errors.append(
            "zero-target guard is not connected to an INFO result"
        )

    if errors:
        print(
            f"[FAIL] v4.0.2 zero-target regression: "
            f"{len(errors)} error(s)"
        )

        for error in errors:
            print(f" - {error}")

        return 1

    print(
        "[PASS] v4.0.2 zero-target regression: "
        "10 machine-dependent controls cannot return PASS "
        "when the Arc machine inventory is empty"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())