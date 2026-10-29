#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def embedded(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/json" id="canonical-assessment">(.*?)</script>', text, re.DOTALL)
    if not match:
        raise AssertionError(f"{path}: canonical JSON missing")
    return json.loads(match.group(1))


def section_ids(path: Path) -> set[str]:
    return set(re.findall(r'<section class="section" id="([^"]+)">', path.read_text(encoding="utf-8")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--en", required=True, type=Path)
    parser.add_argument("--pt", required=True, type=Path)
    args = parser.parse_args()
    en_doc, pt_doc = embedded(args.en), embedded(args.pt)
    if en_doc != pt_doc:
        print("[FAIL] localized reports do not embed the same canonical contract")
        return 1
    if section_ids(args.en) != section_ids(args.pt):
        print("[FAIL] localized reports have different section structures")
        return 1
    en = args.en.read_text(encoding="utf-8")
    pt = args.pt.read_text(encoding="utf-8")
    required = [("Overview", en), ("Visão geral", pt), ("No baseline was supplied", en), ("Nenhum baseline foi fornecido", pt)]
    missing = [label for label, text in required if label not in text]
    if missing:
        print("[FAIL] localization markers missing: " + ", ".join(missing))
        return 1
    print("[PASS] Checkpoint 6 EN-US/PT-BR structure and canonical-data parity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
