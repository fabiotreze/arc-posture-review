#!/usr/bin/env python3
"""Single repository-root gate for APR v4: CP1-CP4.1, CP5 and CLI wrappers."""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSURANCE = ROOT / "assurance" / "v4"
FIXTURE = ROOT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"


def run(label, command):
    print(f"> [{label}] " + " ".join(map(str, command)), flush=True)
    return subprocess.run(command, cwd=ROOT, text=True).returncode == 0


def cleanup():
    for cp in ASSURANCE.glob("checkpoint*"):
        shutil.rmtree(cp / "reports", ignore_errors=True)
    for base in (ASSURANCE, ROOT / "tools"):
        for path in base.rglob("__pycache__"):
            shutil.rmtree(path, ignore_errors=True)


def git_status():
    """Return the sorted porcelain status lines."""
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError("git status failed: " + result.stderr.strip())
    return sorted(line for line in result.stdout.splitlines() if line.strip())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wrapper_smoke():
    pwsh = shutil.which("pwsh")
    if not pwsh:
        print("[FAIL] CLI wrappers: pwsh was not found")
        return False
    with tempfile.TemporaryDirectory() as tmp:
        direct = Path(tmp) / "result.json"
        pipeline = Path(tmp) / "pipeline.json"
        steps = [
            ("wrapper-evaluate", [pwsh, "-NoProfile", "-File", str(ROOT / "arc-posture.ps1"),
                                  "evaluate", "-Evidence", str(FIXTURE), "-Output", str(direct)]),
            ("wrapper-pipeline", [pwsh, "-NoProfile", "-File", str(ROOT / "Invoke-AssessmentPipeline.ps1"),
                                  "-CollectorOutput", str(FIXTURE), "-Output", str(pipeline)]),
        ]
        for label, command in steps:
            if not run(label, command):
                print(f"[FAIL] CLI wrappers: {label}")
                return False
        if sha256(direct) != sha256(pipeline):
            print("[FAIL] CLI wrappers: evaluate and pipeline outputs differ")
            return False
    print("[PASS] CLI wrappers: evaluate and pipeline produce identical output")
    return True


def main():
    cleanup()
    before = git_status()
    failures = []
    steps = [
        ("cp1-to-cp4.1", [sys.executable, str(ASSURANCE / "checkpoint4" / "scripts" / "Invoke-AllGates.py")]),
        ("cp5", [sys.executable, str(ASSURANCE / "checkpoint5" / "scripts" / "Invoke-AllGates.py")]),
    ]
    try:
        for label, command in steps:
            if not run(label, command):
                failures.append(label)
        if not wrapper_smoke():
            failures.append("cli-wrappers")
    finally:
        cleanup()
    after = git_status()
    if before != after:
        failures.append("working-tree-changed-by-gate")
        print("[FAIL] the gate changed the working tree")
        for line in sorted(set(after) ^ set(before)):
            print(" - " + line)
    else:
        print("[PASS] gate left the working tree exactly as it found it")
    if failures:
        print("[FAIL] APR V4 GATES - " + ", ".join(failures))
        return 1
    print("[PASS] APR V4 GATES - CP1-CP5 AND CLI WRAPPERS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
