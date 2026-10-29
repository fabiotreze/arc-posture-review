#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RELEASE = ROOT / "release/v4.0.0"


def main() -> int:
    errors: list[str] = []
    manifest = json.loads((RELEASE / "release-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("release") != "v4.0.0" or manifest.get("status") != "APPROVED_FOR_PUBLICATION":
        errors.append("release manifest status drift")
    if manifest.get("publishable") is not True or (manifest.get("securityReview") or {}).get("decision") != "APPROVED" or not (manifest.get("securityReview") or {}).get("reviewer") or not (manifest.get("securityReview") or {}).get("date"):
        errors.append("stable release is publishable only with an APPROVED securityReview (reviewer and date)")
    blockers = {item.get("id"): item for item in manifest.get("blockers", [])}
    if "KI-V4-001" in blockers:
        errors.append("KI-V4-001 must not remain an open blocker after remediation")
    resolved = {item.get("id"): item for item in manifest.get("resolvedBlockers", [])}
    issue = resolved.get("KI-V4-001", {})
    if issue.get("status") != "RESOLVED" or issue.get("dependency") != "pypdf==6.21.2" or issue.get("previousDependency") != "pypdf==6.19.0" or issue.get("dependabotAlerts") != 11:
        errors.append("KI-V4-001 resolution record drift")
    sums = RELEASE / "SHA256SUMS"
    seen: set[str] = set()
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"malformed SHA256SUMS line: {line}"); continue
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"SHA256SUMS target missing: {relative}"); continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected: errors.append(f"SHA256 mismatch: {relative}")
        if relative in seen: errors.append(f"duplicate checksum target: {relative}")
        seen.add(relative)
    required = {"release/v4.0.0/release-manifest.json", "release/v4.0.0/RELEASE-NOTES.md", "docs/v4/methodology-v4.md", "tools/Invoke-V4FinalGates.py"}
    if not required <= seen: errors.append(f"checksum coverage missing: {sorted(required - seen)}")
    if errors:
        print(f"[FAIL] CP10 release preparation: {len(errors)} error(s)")
        for error in errors: print(" - " + error)
        return 1
    print(f"[PASS] CP10 v4.0.0 APPROVED_FOR_PUBLICATION manifest and {len(seen)} SHA-256 entries")
    return 0


if __name__ == "__main__": raise SystemExit(main())
