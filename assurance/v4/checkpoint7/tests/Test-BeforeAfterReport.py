#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "assurance/v4/checkpoint5/tests"))
from test_lib import evaluate, fixture, mutated, row  # noqa: E402


def mutate_after(document):
    row(document, "CHK-23").update(status="PASS", evidenceCoverage="FULL", found=0, detail="Extension policy is enforced.")
    row(document, "CHK-07").update(status="FAIL", evidenceCoverage="FULL", found=1, detail="An essential provider is not registered.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    before = fixture()
    after = mutated(before, mutate_after)
    document = evaluate(after, before)
    comparison = document.get("comparison")
    errors: list[str] = []
    if comparison is None:
        errors.append("comparison is null")
    elif comparison["summary"] != {"IMPROVED": 1, "REGRESSED": 1, "UNCHANGED": 62}:
        errors.append(f'comparison summary drift: {comparison["summary"]}')
    if comparison:
        by_check = {item["checkId"]: item for item in comparison["controls"]}
        if by_check["CHK-23"]["change"] != "IMPROVED": errors.append("CHK-23 is not improved")
        if by_check["CHK-07"]["change"] != "REGRESSED": errors.append("CHK-07 is not regressed")
    if errors:
        print("[FAIL] CP7 comparison fixture: " + "; ".join(errors))
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("[PASS] CP7 canonical before/after: one Verified Improvement, one regression, 62 unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
