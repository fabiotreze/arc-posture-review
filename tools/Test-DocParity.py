#!/usr/bin/env python3
"""EN-US / pt-BR documentation parity: a translation must not lose or change technical content.

Every pair must keep the heading levels, the table shapes, the number of code blocks and the set of URLs.
Pairs in STRICT (written as translations of an English source) must also keep every code block, every inline
code token and every number identical. Single files that carry both languages (CONTRIBUTING, DISCLAIMER, SECURITY)
must have the same number of list items and code blocks in both halves."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (English file, Portuguese file, strict)
PAIRS = [
    ("README.md", "README.pt-BR.md", False),
    ("docs/guide.en-US.md", "docs/guide.pt-BR.md", False),
    ("docs/sources.en-US.md", "docs/sources.pt-BR.md", False),
    ("docs/v4/methodology-v4.md", "docs/v4/methodology-v4.pt-BR.md", True),
    ("docs/v4/threat-model-v4.md", "docs/v4/threat-model-v4.pt-BR.md", True),
    ("docs/v4/query-evidence-matrix.md", "docs/v4/query-evidence-matrix.pt-BR.md", True),
    ("docs/v4/known-issues.md", "docs/v4/known-issues.pt-BR.md", True),
    ("docs/v4.1.1-posture-vs-evidence.md", "docs/v4.1.1-posture-vs-evidence.pt-BR.md", True),
    ("docs/v4.2.0-foundations.md", "docs/v4.2.0-foundations.pt-BR.md", True),
]
# files with an English half followed by a Portuguese half: (file, marker that starts the Portuguese half)
BILINGUAL = [
    ("CONTRIBUTING.md", "## Contribuindo"),
    ("DISCLAIMER.md", "## Aviso legal"),
    ("SECURITY.md", "## Segurança"),
]
TWIN_NAMES = re.compile(r"(sources|query-evidence-matrix|threat-model-v4|methodology-v4|known-issues|v4\.1\.1-posture-vs-evidence|v4\.2\.0-foundations)(\.en-US)?\.(?:pt-BR\.)?md")


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def split_code(text: str) -> tuple[str, list[str]]:
    fences = re.findall(r"```.*?```", text, flags=re.S)
    return re.sub(r"```.*?```", "", text, flags=re.S), fences


def shape(text: str) -> dict:
    prose, fences = split_code(text)
    tables, current = [], 0
    for line in prose.splitlines():
        if line.startswith("|"):
            current += 1
        elif current:
            tables.append(current)
            current = 0
    if current:
        tables.append(current)
    return {
        "headings": [len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s", prose, re.M)],
        "tables": tables,
        "fences": fences,
        "urls": set(re.findall(r"https?://[^\s)>\]`\"']+", text)),
        "items": len(re.findall(r"^\s*(?:[-*]|\d+\.)\s", prose, re.M)),
        "ticks": set(re.findall(r"`([^`\n]+)`", prose)),
        "numbers": sorted(re.findall(r"\d+(?:[.,]\d+)*", re.sub(r"https?://\S+|`[^`]*`|\]\([^)]*\)", "", prose))),
    }


def twin_normal(token: str) -> str:
    return TWIN_NAMES.sub(lambda m: m.group(1) + ".md", token)


def compare(en_rel: str, pt_rel: str, strict: bool) -> list[str]:
    a, b = shape(read(en_rel)), shape(read(pt_rel))
    errors = []
    if a["headings"] != b["headings"]:
        errors.append(f"heading levels differ ({len(a['headings'])} vs {len(b['headings'])})")
    if a["tables"] != b["tables"]:
        errors.append(f"table shapes differ ({a['tables']} vs {b['tables']})")
    if len(a["fences"]) != len(b["fences"]):
        errors.append(f"code blocks differ ({len(a['fences'])} vs {len(b['fences'])})")
    if a["urls"] != b["urls"]:
        errors.append(f"URLs differ: only EN {sorted(a['urls'] - b['urls'])[:3]}, only PT {sorted(b['urls'] - a['urls'])[:3]}")
    if strict:
        if a["fences"] != b["fences"]:
            errors.append("code blocks are not identical")
        if a["items"] != b["items"]:
            errors.append(f"list items differ ({a['items']} vs {b['items']})")
        ea = {twin_normal(t) for t in a["ticks"]}
        eb = {twin_normal(t) for t in b["ticks"]}
        if ea != eb:
            errors.append(f"inline code differs: only EN {sorted(ea - eb)[:4]}, only PT {sorted(eb - ea)[:4]}")
        # the language switch line adds the twin's file name (with the version digits) to the Portuguese file
        na = [n for n in a["numbers"]]
        nb = list(b["numbers"])
        for n in na:
            if n in nb:
                nb.remove(n)
            else:
                errors.append(f"number {n} of the English text is missing in the Portuguese text")
                break
    return errors


def compare_bilingual(rel: str, marker: str) -> list[str]:
    text = read(rel)
    i = text.find(marker)
    if i < 0:
        return [f"marker {marker!r} not found"]
    en, pt = text[:i], text[i:]
    a, b = shape(en), shape(pt)
    errors = []
    if a["items"] != b["items"]:
        errors.append(f"list items differ ({a['items']} vs {b['items']})")
    if len(a["fences"]) != len(b["fences"]):
        errors.append(f"code blocks differ ({len(a['fences'])} vs {len(b['fences'])})")
    elif a["fences"] != b["fences"]:
        errors.append("code blocks are not identical")
    return errors


def main() -> int:
    failures = []
    for en_rel, pt_rel, strict in PAIRS:
        for message in compare(en_rel, pt_rel, strict):
            failures.append(f"{pt_rel}: {message}")
    for rel, marker in BILINGUAL:
        for message in compare_bilingual(rel, marker):
            failures.append(f"{rel}: {message}")
    if failures:
        print(f"[FAIL] documentation parity: {len(failures)} problem(s)")
        for line in failures:
            print(" - " + line)
        return 1
    print(f"[PASS] documentation parity: {len(PAIRS)} EN/PT pairs ({sum(1 for p in PAIRS if p[2])} strict) and {len(BILINGUAL)} bilingual files keep structure, URLs and code")
    return 0


if __name__ == "__main__":
    sys.exit(main())
