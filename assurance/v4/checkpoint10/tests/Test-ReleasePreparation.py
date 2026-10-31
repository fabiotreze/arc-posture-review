#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKPOINT = ROOT / "assurance/v4/checkpoint10/manifest.json"


def main() -> int:
    errors: list[str] = []
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    release_name = str(checkpoint.get("release", ""))
    if not re.fullmatch(r"v\d+\.\d+\.\d+", release_name):
        print(f"[FAIL] CP10 invalid target release: {release_name!r}")
        return 1
    release = ROOT / "release" / release_name
    manifest_path = release / "release-manifest.json"
    notes_path = release / "RELEASE-NOTES.md"
    sums_path = release / "SHA256SUMS"
    for path in (manifest_path, notes_path, sums_path):
        if not path.is_file():
            errors.append(f"missing release artifact: {path.relative_to(ROOT)}")
    if errors:
        return finish(errors, release_name, 0)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("release") != release_name:
        errors.append("release manifest does not match the checkpoint 10 target")
    status = manifest.get("status")
    publishable = manifest.get("publishable")
    blockers = {row.get("id") for row in manifest.get("blockers", [])}
    review = manifest.get("securityReview", {})

    if status == "VALIDATED_ARTIFACT":
        if publishable is not False:
            errors.append("VALIDATED_ARTIFACT must be non-publishable")
        if "GIT-PROVENANCE-001" not in blockers:
            errors.append("Git provenance blocker is missing")
    elif status == "APPROVED_FOR_PUBLICATION":
        if publishable is not True:
            errors.append("APPROVED_FOR_PUBLICATION must be publishable")
        if blockers:
            errors.append("APPROVED_FOR_PUBLICATION must have no blockers")
        if review.get("decision") != "APPROVED":
            errors.append("APPROVED_FOR_PUBLICATION requires approved security review")
    else:
        errors.append(f"unsupported release status: {status!r}")

    if manifest.get("sourceBranch") != "feature/v4.1.0":
        errors.append("v4.1.0 source branch drift")
    seen: set[str] = set()
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"malformed SHA256SUMS line: {line}")
            continue
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"SHA256SUMS target missing: {relative}")
            continue
        # Release checksums are platform-stable: Git stores text with LF while a
        # Windows checkout can materialize CRLF according to .gitattributes.
        actual = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if actual != expected:
            errors.append(f"SHA256 mismatch: {relative}")
        if relative in seen:
            errors.append(f"duplicate checksum target: {relative}")
        seen.add(relative)
    required = {
        f"release/{release_name}/release-manifest.json",
        f"release/{release_name}/RELEASE-NOTES.md",
        "scripts/Invoke-ArcPostureReview.ps1",
        "assurance/v4/checkpoint4/engine/deterministic_engine.py",
        "assurance/v4/checkpoint5/engine/canonical_v4.py",
        "assurance/v4/checkpoint6/report/render_v4.py",
        "docs/v4/query-evidence-matrix.md",
        "tools/Invoke-V4FinalGates.py",
        "tools/Test-ZeroTarget.py",
        "tools/Test-ZeroConnectedEstate.py",
        "tools/Test-GuideVersion.py",
        "tools/Test-EvidenceHardening.py",
        "docs/v4.1.0-evidence-hardening.md",
        "docs/v4/security-review-record-v4.1.0.md",
        "tests/fixtures/evidence-hardening-negative.v4.1.0.json",
        "tests/fixtures/reviewed-lab-sanitized.zip",
        "tests/fixtures/zero-connected-estate.v4.0.3.json",
    }
    if not required <= seen:
        errors.append(f"checksum coverage missing: {sorted(required - seen)}")
    collector = (ROOT / "scripts/Invoke-ArcPostureReview.ps1").read_text(encoding="utf-8-sig")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    version = release_name.removeprefix("v")
    if f"$ScriptVersion = '{release_name}'" not in collector:
        errors.append("collector version does not match release")
    if f'version: "{version}"' not in citation:
        errors.append("CITATION version does not match release")
    return finish(errors, release_name, len(seen))


def finish(errors: list[str], release_name: str, count: int) -> int:
    if errors:
        print(f"[FAIL] CP10 release preparation: {len(errors)} error(s)")
        for error in errors:
            print(" - " + error)
        return 1
    print(f"[PASS] CP10 {release_name} VALIDATED_ARTIFACT manifest and {count} SHA-256 entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
