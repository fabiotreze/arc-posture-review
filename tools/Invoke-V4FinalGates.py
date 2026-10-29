#!/usr/bin/env python3
"""CP6-CP10 gate orchestrator that preserves the existing tools/Invoke-V4Gates.py."""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "reports", "build"}


def manifest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED for part in relative.parts): continue
        if path.is_file(): result[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def run(label: str, command: list[str], root: Path) -> bool:
    print(f"> [{label}] " + " ".join(command), flush=True)
    return subprocess.run(command, cwd=root, text=True).returncode == 0


def steps(profile: str) -> list[tuple[str, list[str]]]:
    existing = ("checkpoints-1-to-5.1-and-legacy-v3.9.6", [sys.executable, "tools/Invoke-V4Gates.py"])
    cp6 = ("checkpoint6-report", [sys.executable, "assurance/v4/checkpoint6/scripts/Invoke-AllGates.py"])
    cp7 = ("checkpoint7-comparison", [sys.executable, "assurance/v4/checkpoint7/scripts/Invoke-AllGates.py"])
    cp8 = ("checkpoint8-devsecops", [sys.executable, "assurance/v4/checkpoint8/scripts/Invoke-AllGates.py"])
    cp9 = ("checkpoint9-security-review", [sys.executable, "assurance/v4/checkpoint9/scripts/Invoke-AllGates.py"])
    cp10 = ("checkpoint10-release-preparation", [sys.executable, "assurance/v4/checkpoint10/scripts/Invoke-AllGates.py"])
    syntax = ("v4-syntax", [sys.executable, "tools/Test-V4Syntax.py"])
    profiles = {
        "pr-quality": [existing, cp8, cp9, cp10, syntax],
        "methodology": [cp8, cp9, cp10, syntax],
        "security-regression": [existing, cp9, syntax],
        "report-quality": [existing, cp6, cp7, syntax],
        "release": [existing, cp6, cp7, cp8, cp9, cp10, syntax],
        "all": [existing, cp6, cp7, cp8, cp9, cp10, syntax],
    }
    return profiles[profile]


def cleanup(root: Path) -> None:
    for name in ("reports", "build", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"):
        for path in sorted(root.rglob(name), key=lambda item: len(item.parts), reverse=True):
            if path.is_dir(): shutil.rmtree(path)
    for pattern in ("*.pyc", "*.pyo"):
        for path in root.rglob(pattern): path.unlink(missing_ok=True)


def in_place(profile: str) -> int:
    required = ["tools/Invoke-V4Gates.py", "assurance/v4/checkpoint6/scripts/Invoke-AllGates.py", "assurance/v4/checkpoint10/scripts/Invoke-AllGates.py"]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        print("[FAIL] missing integrated files: " + ", ".join(missing)); return 1
    failures: list[str] = []
    try:
        for label, command in steps(profile):
            if not run(label, command, ROOT): failures.append(label)
    finally:
        cleanup(ROOT)
    if failures:
        print("[FAIL] V4 FINAL GATES: " + ", ".join(failures)); return 1
    print(f"[PASS] V4 FINAL GATES profile={profile}")
    return 0


def isolated(profile: str) -> int:
    before = manifest(ROOT)
    with tempfile.TemporaryDirectory(prefix="arc-posture-v4-final-") as temp:
        target = Path(temp) / "repository"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "reports", "build"))
        result = subprocess.run([sys.executable, str(target / "tools/Invoke-V4FinalGates.py"), "--profile", profile, "--in-place"], cwd=target, text=True)
    after = manifest(ROOT)
    if before != after:
        print("[FAIL] source working tree content changed during gates"); return 1
    if result.returncode: return result.returncode
    print("[PASS] working tree content exactly preserved")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("all", "pr-quality", "methodology", "security-regression", "report-quality", "release"), default="all")
    parser.add_argument("--in-place", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    return in_place(args.profile) if args.in_place else isolated(args.profile)


if __name__ == "__main__": raise SystemExit(main())
