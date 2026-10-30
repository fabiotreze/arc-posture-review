#!/usr/bin/env python3
# Local release-preparation helper. Writes only inside the repository; never tags, pushes or publishes.
#   python tools/Prepare-Release.py checksums
#   python tools/Prepare-Release.py approve --reviewer "Full Name"
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CP10 = ROOT / "assurance/v4/checkpoint10/manifest.json"


def jload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def jsave(path: Path, data: dict) -> None:
    path.write_bytes((json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def target() -> tuple[str, Path]:
    release = jload(CP10)["release"]
    if not re.fullmatch(r"v\d+\.\d+\.\d+", release):
        sys.exit(f"[FAIL] invalid checkpoint 10 release: {release}")
    return release, ROOT / "release" / release


def digest(path: Path) -> str:
    # Canonical digest = LF-normalised content (= git blob for text files), identical on Windows (autocrlf) and Linux runners.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def checksums() -> int:
    release, folder = target()
    manifest = jload(folder / "release-manifest.json")
    paths = [f"release/{release}/release-manifest.json", f"release/{release}/RELEASE-NOTES.md", *manifest.get("checksumTargets", [])]
    lines = []
    for rel in dict.fromkeys(paths):
        path = ROOT / rel
        if not path.is_file():
            sys.exit(f"[FAIL] checksum target missing: {rel}")
        lines.append(f"{digest(path)}  {rel}")
    (folder / "SHA256SUMS").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    print(f"[OK] release/{release}/SHA256SUMS: {len(lines)} entries")
    return 0


def approve(reviewer: str) -> int:
    release, folder = target()
    manifest = jload(folder / "release-manifest.json")
    review = manifest["securityReview"]
    record = ROOT / review["record"]
    text = record.read_text(encoding="utf-8")
    done = len(re.findall(r"^\s*- \[[xX]\]", text, re.M))
    todo = len(re.findall(r"^\s*- \[ \]", text, re.M))
    if todo or not done:
        sys.exit(f"[FAIL] {review['record']}: {todo} unchecked, {done} checked; approval refused")
    other = [b.get("id") for b in manifest.get("blockers", []) if not str(b.get("id", "")).endswith("-REVIEW")]
    if other:
        sys.exit(f"[FAIL] open blockers remain: {other}")
    today = datetime.date.today().isoformat()
    record.write_bytes(re.sub(r"^\*\*Decision:\*\* PENDING.*$", f"**Decision:** APPROVED — {reviewer}, {today} ({done}/{done})", text, flags=re.M).encode("utf-8"))
    notes = folder / "RELEASE-NOTES.md"
    notes.write_bytes(re.sub(r"^\*\*Status:\*\* .*$", f"**Status:** APPROVED_FOR_PUBLICATION — security review approved by {reviewer} on {today} ({done}/{done}). Tagging and publishing remain a separate, manual step.", notes.read_text(encoding="utf-8"), flags=re.M).encode("utf-8"))
    manifest.update(status="APPROVED_FOR_PUBLICATION", publishable=True, blockers=[])
    review.update(reviewer=reviewer, date=today, decision="APPROVED", items=done, itemsApproved=done)
    jsave(folder / "release-manifest.json", manifest)
    cp10 = jload(CP10); cp10["status"] = "APPROVED_FOR_PUBLICATION"; jsave(CP10, cp10)
    print(f"[OK] {release} APPROVED_FOR_PUBLICATION by {reviewer} on {today} ({done}/{done})")
    return checksums()


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("checksums")
    ap = sub.add_parser("approve")
    ap.add_argument("--reviewer", required=True)
    args = parser.parse_args()
    return checksums() if args.cmd == "checksums" else approve(args.reviewer)


if __name__ == "__main__": raise SystemExit(main())
