#!/usr/bin/env python3
"""Release checksum targets must be stored with LF in the index.

`sha256sum -c release/<version>/SHA256SUMS` runs on a Linux checkout in the release workflow, where a blob stored with CRLF
(or a file that Git treats as binary because of a lone CR) hashes differently from the LF-normalized digest in the manifest.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
release = json.loads((ROOT / "assurance/v4/checkpoint10/manifest.json").read_text(encoding="utf-8"))["release"]
manifest = json.loads((ROOT / "release" / release / "release-manifest.json").read_text(encoding="utf-8"))
targets = {*manifest.get("checksumTargets", []), f"release/{release}/release-manifest.json", f"release/{release}/RELEASE-NOTES.md"}
probe = subprocess.run(["git", "ls-files", "--eol"], cwd=ROOT, capture_output=True, text=True)
# The final gate runs in a copy that is not a Git repository: only the lone-CR check applies there.
eol = probe.stdout.splitlines() if probe.returncode == 0 else []
errors = []
for line in eol:
    info, _, path = line.partition("\t")
    if path.endswith((".png", ".pdf", ".zip")):
        continue
    index_eol = info.split()[0]
    if path in targets and index_eol == "i/crlf":
        errors.append(f"{path}: stored with CRLF in the index (Linux sha256sum would not match)")
    if index_eol == "i/-text" and path.endswith((".ps1", ".py", ".md", ".json", ".yml", ".html", ".txt", ".cff", ".psd1")):
        errors.append(f"{path}: Git treats this text file as binary (look for a lone CR)")
for path in sorted(targets):
    full = ROOT / path
    if full.is_file() and not path.endswith((".zip", ".png", ".pdf")) and re.search(rb"\r(?!\n)", full.read_bytes()):
        errors.append(f"{path}: contains a lone CR")
print(("FAIL" if errors else "PASS") + " line endings: " + ("; ".join(errors) if errors else f"{len(targets)} release checksum targets are LF in the index and have no lone CR"))
sys.exit(1 if errors else 0)
