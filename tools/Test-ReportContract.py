#!/usr/bin/env python3
"""Deterministic contract checks for the app, collector and saved HTML reports."""
from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "4.0.4"


class OutlineParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.headings: list[str] = []
        self._heading: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if values.get("href", "").startswith("#"):
            self.hrefs.append((values["href"] or "")[1:])
        if tag in {"h1", "h2", "h3", "h4"}:
            self._heading = []

    def handle_data(self, data: str) -> None:
        if self._heading is not None:
            self._heading.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4"} and self._heading is not None:
            self.headings.append(" ".join("".join(self._heading).split()))
            self._heading = None


def fail(message: str) -> None:
    raise AssertionError(message)


def between(text: str, begin: str, end: str) -> str:
    match = re.search(re.escape(begin) + r"\n?(.*?)\n?" + re.escape(end), text, re.DOTALL)
    if not match:
        fail(f"missing generated block {begin}")
    return match.group(1)


def json_var(text: str, name: str):
    match = re.search(r"var\s+" + re.escape(name) + r"\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not match:
        fail(f"missing JSON variable {name}")
    return json.loads(match.group(1))


def check_version() -> None:
    script = (ROOT / "scripts/Invoke-ArcPostureReview.ps1").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    guide_en = (ROOT / "docs/guide.en-US.md").read_text(encoding="utf-8")
    guide_pt = (ROOT / "docs/guide.pt-BR.md").read_text(encoding="utf-8")
    values = {
        "collector": re.search(r"\$ScriptVersion = 'v([0-9.]+)'", script).group(1),
        "CHANGELOG": re.search(r"^## \[([0-9.]+)\]", changelog, re.MULTILINE).group(1),
        "CITATION": re.search(r'^version: "([0-9.]+)"', citation, re.MULTILINE).group(1),
        "guide.en-US": re.search(r"\*\*Version v([0-9.]+)", guide_en).group(1),
        "guide.pt-BR": re.search(r"\*\*Versão v([0-9.]+)", guide_pt).group(1),
    }
    if set(values.values()) != {EXPECTED_VERSION}:
        fail(f"version drift: {values}")


def check_app(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if f'var VERSION = "v{EXPECTED_VERSION}";' not in text:
        fail(f"{path.name}: runtime version mismatch")
    if text.count("uxActHtml(x.it)") != 1:
        fail(f"{path.name}: action guidance must be emitted exactly once")
    if "btnGuideMd" in text or 'id="mdSource"' in text or "arc-posture-review-guide." in text:
        fail(f"{path.name}: retired Markdown guide surface is still present")
    if re.search(r'<a\b[^>]*\b(?:download|href)="[^"]*\.md(?:[?#][^"]*)?"', text, re.IGNORECASE):
        fail(f"{path.name}: Guide/report Markdown download link was reintroduced")
    canonical = "Canonical guide" if path.name.endswith("en-US.html") else "Guia canônico"
    if canonical not in text:
        fail(f"{path.name}: canonical integrated-guide marker missing")
    if "script-src \\'sha256-' + SNAPSHOT_RUNTIME_HASH" not in text:
        fail(f"{path.name}: saved-report CSP does not use the runtime hash")
    if 'SNAPSHOT_RUNTIME + "<\\/script>' not in text:
        fail(f"{path.name}: saved-report runtime closing tag is not HTML-parser safe")
    embedded = re.search(r'<script type="text/plain" id="psTemplate">(.*?)</script>', text, re.DOTALL)
    collector = (ROOT / "scripts/Invoke-ArcPostureReview.ps1").read_text(encoding="utf-8").rstrip() + "\n"
    if not embedded or embedded.group(1) != collector:
        fail(f"{path.name}: embedded collector drift")
    items = json_var(text, "ITEMS")
    alerts = json_var(text, "ALERTS")
    ids = [item["id"] for item in items]
    if len(items) != 64 or len(ids) != len(set(ids)):
        fail(f"{path.name}: expected 64 unique checks, found {len(items)}")
    if len(alerts) != 9:
        fail(f"{path.name}: expected 9 alert definitions, found {len(alerts)}")
    required_contract = [
        "evidenceCoverage", "coverageStats", "Evidence contract by check" if path.name.endswith("en-US.html") else "Contrato de evidência por verificação",
        "Assessment Coverage" if path.name.endswith("en-US.html") else "Cobertura da avaliação",
        "Score before rounding" if path.name.endswith("en-US.html") else "Nota antes do arredondamento",
        'class=\"full-evidence\"', "MDE extension deployed through Arc" if path.name.endswith("en-US.html") else "Extensão MDE implantada pelo Arc",
        "Executive assessment" if path.name.endswith("en-US.html") else "Avaliação executiva",
        "Evidence appendix" if path.name.endswith("en-US.html") else "Apêndice de evidências",
        "Open the official project Guide (HTML)" if path.name.endswith("en-US.html") else "Abrir o Guide oficial do projeto (HTML)",
        "displayed values are rounded" if path.name.endswith("en-US.html") else "valores exibidos arredondados",
        "print-ultrawide", "@page { size: landscape; margin: 8mm; }",
        'previewLimit = d.id === "pr-CHK-33" ? 10 : 50',
    ]
    missing = [marker for marker in required_contract if marker not in text]
    if missing:
        fail(f"{path.name}: reviewed-lab contract markers missing: {missing}")
    if re.search(r"\.st-ERRO(?!R)|\.st-PARCIAL|<option>ERRO</option>|<option>PARCIAL</option>", text):
        fail(f"{path.name}: legacy ERRO/PARCIAL presentation remains")
    runtime_match = re.search(r"var SNAPSHOT_RUNTIME = (\"(?:\\.|[^\"])*\");\n  var SNAPSHOT_RUNTIME_HASH = \"([^\"]+)\";", text)
    if not runtime_match:
        fail(f"{path.name}: synchronized runtime constants not found")
    runtime = json.loads(runtime_match.group(1))
    digest = base64.b64encode(hashlib.sha256(runtime.encode("utf-8")).digest()).decode("ascii")
    if digest != runtime_match.group(2):
        fail(f"{path.name}: report runtime hash mismatch")


def check_sample(path: Path, required: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if f"checklist v{EXPECTED_VERSION}" not in text:
        fail(f"{path.name}: sample version mismatch")
    guide_label = "Open the official project Guide (HTML)" if path.name.endswith("en-US.html") else "Abrir o Guide oficial do projeto (HTML)"
    rounding_label = "displayed values are rounded" if path.name.endswith("en-US.html") else "valores exibidos arredondados"
    for marker in (guide_label, rounding_label, "print-ultrawide"):
        if marker not in text:
            fail(f"{path.name}: v{EXPECTED_VERSION} gate marker missing: {marker}")
    guide_href = re.search(r'<nav class="official-guide-access"[^>]*>\s*<a href="([^"]+\.html)"', text)
    if not guide_href or not (path.parent / guide_href.group(1)).resolve().is_file():
        fail(f"{path.name}: Guide HTML target is missing or broken")
    if re.search(r'<a\b[^>]*\b(?:download|href)="[^"]*\.md(?:[?#][^"]*)?"', text, re.IGNORECASE):
        fail(f"{path.name}: Markdown download link was reintroduced")
    runtime = (ROOT / "tools/report-runtime.js").read_text(encoding="utf-8").rstrip() + "\n"
    digest = base64.b64encode(hashlib.sha256(runtime.encode("utf-8")).digest()).decode("ascii")
    if f"script-src 'sha256-{digest}'" not in text:
        fail(f"{path.name}: CSP runtime hash missing")
    script = re.search(r'<script id="arc-report-runtime">(.*?)</script>', text, re.DOTALL)
    if not script or script.group(1) != runtime:
        fail(f"{path.name}: saved runtime drift")
    if re.search(r'<(?:script|img|link)\b[^>]*(?:src|href)="https?://', text, re.IGNORECASE):
        fail(f"{path.name}: external executable/resource reference found")
    copy_count = len(re.findall(r'class="[^"]*\bcopyk\b', text))
    pair_count = len(re.findall(r'<pre class="code">.*?</pre><button class="btn copyk"', text, re.DOTALL))
    if copy_count == 0 or copy_count != pair_count:
        fail(f"{path.name}: {copy_count} copy buttons but {pair_count} adjacent code blocks")
    chunks = re.split(r'<details class="pr"', text)[1:]
    if not chunks:
        fail(f"{path.name}: no priority details")
    for index, chunk in enumerate(chunks, 1):
        segment = chunk.split('<details class="pr"', 1)[0]
        if segment.count('class="actbox"') != 1:
            fail(f"{path.name}: priority {index} does not contain exactly one action block")
    parser = OutlineParser()
    parser.feed(text)
    missing_targets = sorted({target for target in parser.hrefs if target and target not in parser.ids})
    if missing_targets:
        fail(f"{path.name}: broken internal targets: {missing_targets[:8]}")
    cursor = -1
    for heading in required:
        try:
            cursor = parser.headings.index(heading, cursor + 1)
        except ValueError:
            fail(f"{path.name}: required heading out of order or missing: {heading}")
    if re.search(r'<(?:a|div)\b[^>]*\btabindex="0"[^>]*>(?:CHK|ALR|guia|guide)', text, re.IGNORECASE):
        fail(f"{path.name}: inert exported navigation remains keyboard-focusable")


def main() -> int:
    try:
        check_version()
        en = ROOT / "arc-posture-review.en-US.html"
        pt = ROOT / "arc-posture-review.pt-BR.html"
        check_app(en)
        check_app(pt)
        if (ROOT / "index.html").read_bytes() != en.read_bytes():
            fail("index.html must be byte-identical to arc-posture-review.en-US.html")
        css = (ROOT / "tools/report-responsive.css").read_text(encoding="utf-8").rstrip()
        for path in [en, pt, ROOT / "index.html", ROOT / "docs/examples/sample-analysis.en-US.html", ROOT / "docs/examples/sample-analysis.pt-BR.html"]:
            block = between(path.read_text(encoding="utf-8"), "  /* REPORT_RESPONSIVE_BEGIN */", "  /* REPORT_RESPONSIVE_END */")
            normalized = "\n".join(line[2:] if line.startswith("  ") else line for line in block.splitlines()).rstrip()
            if normalized != css:
                fail(f"{path.name}: responsive CSS drift")
        check_sample(
            ROOT / "docs/examples/sample-analysis.en-US.html",
            ["Quick read", "Executive assessment", "What to do now", "Compliance by layer and MCSB control", "Fleet indicators", "Evidence appendix", "Collection account permissions", "How the metrics are calculated", "Priorities (24)", "By subscription", "Cross-subscription scenarios", "What was not assessed or is informational (38)", "Assessment of each collected file", "Checklist record"],
        )
        check_sample(
            ROOT / "docs/examples/sample-analysis.pt-BR.html",
            ["Leitura rápida", "Avaliação executiva", "O que fazer agora", "Conformidade por camada e controle MCSB", "Indicadores do parque", "Apêndice de evidências", "Permissões da conta de coleta", "Como as métricas são calculadas", "Prioridades (24)", "Por subscription", "Cenários cross-subscription", "O que não foi avaliado ou é informativo (38)", "Avaliação de cada arquivo coletado", "Registro do checklist"],
        )
    except (AssertionError, AttributeError, json.JSONDecodeError) as exc:
        print("FAIL", exc)
        return 1
    print("PASS report contract: version, schema, CSP, structure, navigation and bilingual parity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
