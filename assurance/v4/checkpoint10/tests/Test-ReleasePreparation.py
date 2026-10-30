#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CP10 = ROOT / "assurance/v4/checkpoint10"


def main() -> int:
    errors: list[str] = []
    cp10 = json.loads((CP10 / "manifest.json").read_text(encoding="utf-8"))
    release = str(cp10.get("release", ""))
    if not re.fullmatch(r"v\d+\.\d+\.\d+", release):
        print(f"[FAIL] CP10 invalid target release: {release!r}"); return 1
    rel_dir = f"release/{release}"
    manifest = json.loads((ROOT / rel_dir / "release-manifest.json").read_text(encoding="utf-8"))
    review = manifest.get("securityReview") or {}
    if manifest.get("release") != release: errors.append("release manifest does not match the checkpoint 10 target")
    if manifest.get("status") != cp10.get("status"): errors.append("checkpoint 10 / release manifest status drift")
    if manifest.get("publishable") is True:
        if manifest.get("status") != "APPROVED_FOR_PUBLICATION" or review.get("decision") != "APPROVED" or not review.get("reviewer") or not review.get("date"):
            errors.append("publishable requires APPROVED_FOR_PUBLICATION and an APPROVED securityReview with reviewer and date")
        if manifest.get("blockers"): errors.append("a publishable release must have no open blockers")
    elif manifest.get("status") != "PENDING_SECURITY_REVIEW" or review.get("decision") == "APPROVED":
        errors.append("a non-publishable release must be PENDING_SECURITY_REVIEW without an APPROVED decision")
    if "KI-V4-001" in {b.get("id") for b in manifest.get("blockers", [])}:
        errors.append("KI-V4-001 must not remain an open blocker after remediation")
    ki = {b.get("id"): b for b in manifest.get("resolvedBlockers", [])}.get("KI-V4-001", {})
    if ki.get("status") != "RESOLVED" or ki.get("dependency") != "pypdf==6.21.2":
        errors.append("KI-V4-001 resolution record drift")
    version = release[1:]
    ps1 = (ROOT / "scripts/Invoke-ArcPostureReview.ps1").read_text(encoding="utf-8-sig")
    if f"$ScriptVersion = '{release}'" not in ps1: errors.append("collector $ScriptVersion does not match the release")
    if not re.search(r'^version:\s*"?' + re.escape(version) + r'"?\s*$', (ROOT / "CITATION.cff").read_text(encoding="utf-8"), re.M):
        errors.append("CITATION.cff version drift")
    if f"## [{version}]" not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        errors.append(f"CHANGELOG.md has no [{version}] section")
    seen: set[str] = set()
    for line in (ROOT / rel_dir / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"malformed SHA256SUMS line: {line}"); continue
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"SHA256SUMS target missing: {relative}"); continue
        if hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != expected: errors.append(f"SHA256 mismatch (LF-normalised): {relative}")
        if relative in seen: errors.append(f"duplicate checksum target: {relative}")
        seen.add(relative)
    required = {f"{rel_dir}/release-manifest.json", f"{rel_dir}/RELEASE-NOTES.md", "scripts/Invoke-ArcPostureReview.ps1", "docs/v4/methodology-v4.md", "tools/Invoke-V4FinalGates.py"}
    if not required <= seen: errors.append(f"checksum coverage missing: {sorted(required - seen)}")
    if errors:
        print(f"[FAIL] CP10 {release} release preparation: {len(errors)} error(s)")
        for error in errors: print(" - " + error)
        return 1
    state = "APPROVED_FOR_PUBLICATION" if manifest.get("publishable") is True else "PENDING_SECURITY_REVIEW (publication blocked)"
    print(f"[PASS] CP10 {release} {state}; {len(seen)} SHA-256 entries")
    return 0


if __name__ == "__main__": raise SystemExit(main())
