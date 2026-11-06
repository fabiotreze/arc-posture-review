#!/usr/bin/env python3
"""Build the runtime kit that lets the collector produce the canonical v4 report.

The kit is a small, stdlib-only Python bundle (evaluation engine, renderer and the data they read).
It is built deterministically (sorted entries, fixed timestamps, stored without compression, LF text)
so that its SHA-256 can be pinned inside the collector and verified when the collector downloads it.

  python tools/Build-Kit.py                 print the kit SHA-256
  python tools/Build-Kit.py --output F.zip  write the kit
  python tools/Build-Kit.py --write-hash    pin the SHA-256 in scripts/Invoke-ArcPostureReview.ps1
  python tools/Build-Kit.py --check         fail when the pinned SHA-256 is stale
"""
from __future__ import annotations

import argparse
import hashlib
import io
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / "scripts" / "Invoke-ArcPostureReview.ps1"
PIN = re.compile(rb"(\$KitSha256 = ')([0-9A-Fa-f]{64})(')")

KIT_FILES = [
    "VERSION",
    "assurance/v4/checkpoint3/data/action-cards.json",
    "assurance/v4/checkpoint3/data/checks.enriched.json",
    "assurance/v4/checkpoint3/data/control-assessments.json",
    "assurance/v4/checkpoint3/data/defense-coverage.json",
    "assurance/v4/checkpoint3/data/security-scenarios.json",
    "assurance/v4/checkpoint3/data/taxonomies.json",
    "assurance/v4/checkpoint4/engine/__init__.py",
    "assurance/v4/checkpoint4/engine/deterministic_engine.py",
    "assurance/v4/checkpoint4/engine/repository_layout.py",
    "assurance/v4/checkpoint5/cli/arc_posture.py",
    "assurance/v4/checkpoint5/engine/__init__.py",
    "assurance/v4/checkpoint5/engine/canonical_v4.py",
    "assurance/v4/checkpoint6/report/render_v4.py",
    "criteria/v4/check-catalog.v4.json",
    "criteria/v4/pt-br-detail-rules.json",
    "criteria/checks.pt-BR.json",
    "tools/New-ResourceIndex.py",
]
# The engine locates its root by the presence of this directory.
PLACEHOLDERS = ["tests/fixtures/.keep"]
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def build() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as kit:
        for name in sorted([*KIT_FILES, *PLACEHOLDERS]):
            payload = b"" if name in PLACEHOLDERS else (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3  # the header records the build platform; pin it so Windows and Linux produce identical bytes
            info.external_attr = 0o644 << 16
            kit.writestr(info, payload)
    return buffer.getvalue()


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def pinned() -> str:
    match = PIN.search(COLLECTOR.read_bytes())
    if not match:
        sys.exit("[FAIL] $KitSha256 pin not found in the collector")
    return match.group(2).decode("ascii").upper()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write-hash", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    current = digest(payload)
    if args.output:
        args.output.write_bytes(payload)
        print(f"[OK] kit written: {args.output} ({len(payload)} bytes)")
    if args.write_hash:
        raw = COLLECTOR.read_bytes()
        COLLECTOR.write_bytes(PIN.sub(lambda m: m.group(1) + current.encode("ascii") + m.group(3), raw, count=1))
        print(f"[OK] pinned kit SHA-256 in the collector: {current}")
    if args.check:
        if pinned() != current:
            print(f"[FAIL] kit SHA-256 drift: pinned {pinned()} != built {current}. Run: python tools/Build-Kit.py --write-hash")
            return 1
        print(f"[PASS] kit SHA-256 pinned in the collector matches the built kit ({current[:12]}…, {len(KIT_FILES)} files)")
    if not (args.output or args.write_hash or args.check):
        print(current)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
