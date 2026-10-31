#!/usr/bin/env python3
"""Static contract gate for explicit evidence targets and query evidence retention."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / "scripts" / "Invoke-ArcPostureReview.ps1"
ZERO_TARGET_CHECKS = {
    "CHK-12", "CHK-21", "CHK-23", "CHK-24", "CHK-27",
    "CHK-28", "CHK-32", "CHK-37", "CHK-39", "CHK-51",
}


def main() -> int:
    text = COLLECTOR.read_text(encoding="utf-8-sig")
    errors: list[str] = []
    match = re.search(r"\$Catalog\s*=\s*@'\s*(\[.*?\])\s*'@\s*\|\s*ConvertFrom-Json", text, re.S)
    if not match:
        errors.append("collector catalog was not found")
        catalog = []
    else:
        catalog = json.loads(match.group(1))
    automatic = {row["id"] for row in catalog if row["type"] == "auto"}
    eval_blocks = set(re.findall(r"\$Eval\['(CHK-\d{2})'\]\s*=", text))
    if automatic != eval_blocks:
        errors.append(f"automatic/Eval drift: missing={sorted(automatic-eval_blocks)}, extra={sorted(eval_blocks-automatic)}")
    required_markers = (
        "function Set-EvidenceTarget", "function Initialize-EvidenceTarget", "function Finalize-EvidenceTarget",
        "applicableCount = 0", "evaluatedCount = 0", "healthyCount = $null",
        "a zero-target result is N/A, never PASS", "data/query-evidence.json",
        "function Add-QueryEvidence", "statementSha256", "failedScopes",
    )
    for marker in required_markers:
        if marker not in text:
            errors.append(f"missing collector contract marker: {marker}")
    for check_id in sorted(ZERO_TARGET_CHECKS):
        if f"'{check_id}'" not in text:
            errors.append(f"missing zero-target control: {check_id}")
    if "CHK-12" in ZERO_TARGET_CHECKS and "managed-identity RBAC cannot be validated and PASS is prohibited" not in text:
        errors.append("CHK-12 missing-identity guard is absent")
    if "Pagination stopped at the 500-page safety limit" not in text:
        errors.append("Resource Graph pagination truncation is not rejected")
    if errors:
        print(f"[FAIL] zero-target/query-evidence contract: {len(errors)} error(s)")
        for error in errors:
            print(" - " + error)
        return 1
    print(f"[PASS] zero-target/query-evidence contract: {len(automatic)} automatic checks, explicit targets, query ledger, pagination guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
