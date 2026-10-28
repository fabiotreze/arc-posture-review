#!/usr/bin/env python3
"""Synchronize the collector and shared report assets into offline pages/reports."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PAGES = [ROOT / "arc-posture-review.en-US.html", ROOT / "arc-posture-review.pt-BR.html"]
SAMPLES = [ROOT / "docs/examples/sample-analysis.en-US.html", ROOT / "docs/examples/sample-analysis.pt-BR.html"]
CRITERIA = {
    "en-US": ROOT / "criteria/checks.en-US.json",
    "pt-BR": ROOT / "criteria/checks.pt-BR.json",
}
DOMAIN_NAMES = {
    "A": "A · Architecture and scope",
    "B": "B · Governance and identity",
    "C": "C · Connectivity and network",
    "D": "D · Agent, extensions, and protection",
    "E": "E · Operations, monitoring, and auditing",
    "F": "F · Legacy",
}
CSS_BEGIN = "  /* REPORT_RESPONSIVE_BEGIN */"
CSS_END = "  /* REPORT_RESPONSIVE_END */"
RUNTIME_BEGIN = "  // REPORT_RUNTIME_BEGIN"
RUNTIME_END = "  // REPORT_RUNTIME_END"


def replace_block(text: str, begin: str, end: str, replacement: str, before: str) -> str:
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(lambda _match: replacement, text, count=1)
    if before not in text:
        raise ValueError(f"insertion anchor not found: {before}")
    return text.replace(before, replacement + "\n" + before, 1)


def replace_json_var(text: str, name: str, value: object) -> str:
    marker = "var " + name + " = "
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"JSON variable not found: {name}")
    value_start = start + len(marker)
    _old, value_end = json.JSONDecoder().raw_decode(text[value_start:])
    absolute_end = value_start + value_end
    if absolute_end >= len(text) or text[absolute_end] != ";":
        raise ValueError(f"JSON variable terminator not found: {name}")
    rendered = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text[:value_start] + rendered + text[absolute_end:]


def validate_criteria(en_items: list[dict], pt_items: list[dict]) -> None:
    expected = [f"CHK-{number:02d}" for number in range(1, 65)]
    required = {"id", "dom", "sev", "type", "ds", "title", "crit", "resultCriteria", "refs", "key", "layer", "mcsb", "tree", "hz", "owner", "steps", "how"}
    for locale, items in (("en-US", en_items), ("pt-BR", pt_items)):
        ids = [item.get("id") for item in items]
        if ids != expected:
            raise ValueError(f"{locale}: criteria IDs must be CHK-01..CHK-64 in order")
        for item in items:
            missing = required - set(item)
            if missing:
                raise ValueError(f"{locale} {item.get('id')}: missing fields {sorted(missing)}")
    structural = ("id", "dom", "type", "ds", "refs", "key", "layer", "mcsb", "tree", "hz")
    for en_item, pt_item in zip(en_items, pt_items):
        for field in structural:
            if en_item[field] != pt_item[field]:
                raise ValueError(f"criteria locale drift at {en_item['id']}.{field}")


def update_collector(text: str, items: list[dict]) -> str:
    ids = [item["id"] for item in items]
    checks = ", ".join("'" + check_id + "'" for check_id in ids)
    text, count = re.subn(
        r"\[string\[\]\]\$Checks = @\(.*?\),\n  \[string\]\$OutputRoot",
        lambda _match: "[string[]]$Checks = @(" + checks + "),\n  [string]$OutputRoot",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise ValueError("collector Checks parameter not found")
    catalog = [
        {
            "id": item["id"],
            "domain": DOMAIN_NAMES[item["dom"]],
            "title": item["title"],
            "sev": item["sev"],
            "type": item["type"],
            "ds": item["ds"],
            "refs": item["refs"],
        }
        for item in items
    ]
    catalog_json = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
    text, count = re.subn(
        r"\$Catalog = @'\n.*?\n'@ \| ConvertFrom-Json",
        lambda _match: "$Catalog = @'\n" + catalog_json + "\n'@ | ConvertFrom-Json",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise ValueError("collector Catalog block not found")
    return text


def update_app(text: str, css: str, runtime: str, digest: str, collector: str, items: list[dict]) -> str:
    text = replace_json_var(text, "ITEMS", items)
    collector_tag = '<script type="text/plain" id="psTemplate">' + collector.rstrip() + "\n</script>"
    text, count = re.subn(r'<script type="text/plain" id="psTemplate">.*?</script>', lambda _match: collector_tag, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise ValueError("embedded collector psTemplate not found")
    css_block = CSS_BEGIN + "\n" + "\n".join("  " + line if line else "" for line in css.rstrip().splitlines()) + "\n" + CSS_END
    text = replace_block(text, CSS_BEGIN, CSS_END, css_block, "</style>")
    runtime_block = (
        RUNTIME_BEGIN
        + "\n  var SNAPSHOT_RUNTIME = "
        + json.dumps(runtime, ensure_ascii=False)
        + ";\n  var SNAPSHOT_RUNTIME_HASH = "
        + json.dumps(digest)
        + ";\n"
        + RUNTIME_END
    )
    return replace_block(text, RUNTIME_BEGIN, RUNTIME_END, runtime_block, "  async function snapshotHtml(withReport) {")


def update_sample(text: str, css: str, runtime: str, digest: str) -> str:
    css_block = CSS_BEGIN + "\n" + "\n".join("  " + line if line else "" for line in css.rstrip().splitlines()) + "\n" + CSS_END
    text = replace_block(text, CSS_BEGIN, CSS_END, css_block, "</style>")
    csp = "default-src 'none'; script-src 'sha256-" + digest + "'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"
    text, count = re.subn(
        r'<meta\b(?=[^>]*http-equiv="Content-Security-Policy")[^>]*>',
        lambda _match: '<meta http-equiv="Content-Security-Policy" content="' + csp + '">',
        text,
        count=1,
        flags=re.IGNORECASE,
    )
    if count != 1:
        raise ValueError("sample report CSP not found")
    script_tag = '<script id="arc-report-runtime">' + runtime + "</script>"
    text = re.sub(r'<script id="arc-report-runtime">.*?</script>', lambda _match: script_tag, text, count=1, flags=re.DOTALL)
    if 'id="arc-report-runtime"' not in text:
        text = text.replace("</body>", script_tag + "</body>", 1)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail instead of writing when generated assets differ")
    args = parser.parse_args()

    criteria = {locale: json.loads(path.read_text(encoding="utf-8")) for locale, path in CRITERIA.items()}
    validate_criteria(criteria["en-US"], criteria["pt-BR"])
    css = (ROOT / "tools/report-responsive.css").read_text(encoding="utf-8")
    runtime = (ROOT / "tools/report-runtime.js").read_text(encoding="utf-8").rstrip() + "\n"
    collector_path = ROOT / "scripts/Invoke-ArcPostureReview.ps1"
    collector_old = collector_path.read_text(encoding="utf-8")
    collector = update_collector(collector_old, criteria["en-US"])
    digest = base64.b64encode(hashlib.sha256(runtime.encode("utf-8")).digest()).decode("ascii")
    changed: list[Path] = []

    if collector != collector_old:
        changed.append(collector_path)
        if not args.check:
            collector_path.write_text(collector, encoding="utf-8", newline="\n")

    for path in APP_PAGES:
        old = path.read_text(encoding="utf-8")
        locale = "en-US" if path.name.endswith("en-US.html") else "pt-BR"
        new = update_app(old, css, runtime, digest, collector, criteria[locale])
        if new != old:
            changed.append(path)
            if not args.check:
                path.write_text(new, encoding="utf-8", newline="\n")

    for path in SAMPLES:
        old = path.read_text(encoding="utf-8")
        new = update_sample(old, css, runtime, digest)
        if new != old:
            changed.append(path)
            if not args.check:
                path.write_text(new, encoding="utf-8", newline="\n")

    index = ROOT / "index.html"
    en = (ROOT / "arc-posture-review.en-US.html").read_text(encoding="utf-8")
    old_index = index.read_text(encoding="utf-8")
    if old_index != en:
        changed.append(index)
        if not args.check:
            index.write_text(en, encoding="utf-8", newline="\n")

    if changed:
        for path in changed:
            print(("OUT-OF-DATE" if args.check else "UPDATED") + " " + str(path.relative_to(ROOT)))
        return 1 if args.check else 0
    print("Report assets are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
