#!/usr/bin/env python3
"""Embedded guide version markers must match the collector version (no stale 'canonical guide' version)."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT / path).read_text(encoding="utf-8-sig", errors="replace")

m = re.search(r"\$ScriptVersion = 'v(\d+\.\d+\.\d+)'", read("scripts/Invoke-ArcPostureReview.ps1"))
if not m:
    print("FAIL guide version: $ScriptVersion not found in the collector")
    sys.exit(1)
expected = m.group(1)

RULES = [
    ("index.html", r"Canonical project guide for v(\d+\.\d+\.\d+)"),
    ("index.html", r"<strong>Version v(\d+\.\d+\.\d+) "),
    ("arc-posture-review.en-US.html", r"Canonical project guide for v(\d+\.\d+\.\d+)"),
    ("arc-posture-review.en-US.html", r"<strong>Version v(\d+\.\d+\.\d+) "),
    ("arc-posture-review.pt-BR.html", r"Guia can.nico do projeto para a v(\d+\.\d+\.\d+)"),
    ("arc-posture-review.pt-BR.html", r"<strong>Vers.o v(\d+\.\d+\.\d+) "),
    ("docs/guide.en-US.md", r"\*\*Version v(\d+\.\d+\.\d+) "),
    ("docs/guide.pt-BR.md", r"\*\*Vers.o v(\d+\.\d+\.\d+) "),
]

errors = []
for path, pattern in RULES:
    found = re.findall(pattern, read(path))
    if len(found) != 1:
        errors.append(f"{path}: marker /{pattern}/ found {len(found)}x (expected 1)")
    elif found[0] != expected:
        errors.append(f"{path}: version drift v{found[0]} != collector v{expected}")

if errors:
    print("FAIL guide version: " + "; ".join(errors))
    sys.exit(1)
print(f"PASS guide version: {len(RULES)} guide markers in 3 HTML files and 2 guides match collector v{expected}")
