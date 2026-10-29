#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs/v4"


def main() -> int:
    errors: list[str] = []
    required = {
        "methodology-v4.md": ["assessment-result.v4.json", "CHK-01", "CHK-64", "IDENTITY → MANAGEMENT → HOST → DEFENSE", "Verified Improvement"],
        "threat-model-v4.md": ["Trust boundaries", "Missing-evidence optimism", "Attack overclaim", "Dependency exposure"],
        "security-review-checklist.md": ["False-positive review", "comparison: null", "Dependabot", "Stable v4.0.0 remains blocked"],
        "false-positive-review.md": ["Missing evidence", "Verified Improvement", "NOT_ASSERTED"],
        "known-issues.md": ["KI-V4-001", "RESOLVED", "pypdf==6.19.0", "pypdf==6.21.2", "11 Dependabot alerts"],
    }
    for name, markers in required.items():
        path = DOCS / name
        if not path.is_file():
            errors.append(f"missing {name}"); continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text: errors.append(f"{name}: missing {marker}")
    checklist = (DOCS / "security-review-checklist.md").read_text(encoding="utf-8")
    if len(re.findall(r"^- \[ \]", checklist, re.MULTILINE)) < 24:
        errors.append("security checklist has fewer than 24 review items")
    rc = json.loads((ROOT / "release/v4.0.0-rc.1/release-manifest.json").read_text(encoding="utf-8"))
    if rc.get("release") != "v4.0.0-rc.1" or not rc.get("stableReleaseBlocked") or rc.get("blocker") != "KI-V4-001":
        errors.append("RC.1 release manifest blocker contract drift")
    if errors:
        print(f"[FAIL] CP9 security review package: {len(errors)} error(s)")
        for error in errors: print(" - " + error)
        return 1
    print("[PASS] CP9 v4.0.0-rc.1 methodology, threat model, false-positive and security-review package")
    return 0


if __name__ == "__main__": raise SystemExit(main())
