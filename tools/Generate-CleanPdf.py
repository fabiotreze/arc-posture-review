#!/usr/bin/env python3
"""Generate a clean, validated PDF from a saved Arc Posture Review HTML report.

Uses WeasyPrint rather than the browser print dialog, so browser URL/date headers
and footers are never injected. Details are expanded and wide tables are wrapped.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader
from weasyprint import HTML

PRINT_CSS = r"""
@page {
  size: __PAGE_SIZE__;
  margin: 8mm;
  @top-left { content: none; }
  @top-center { content: none; }
  @top-right { content: none; }
  @bottom-left { content: none; }
  @bottom-center { content: none; }
  @bottom-right { content: none; }
}
html, body { width: auto !important; max-width: none !important; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
body { font-size: 9pt !important; }
button, .copyk { display: none !important; }
details > * { display: block !important; }
[hidden] { display: block !important; }
main.wrap, .wrap, .card, .ana, .body, details { width: auto !important; max-width: none !important; min-width: 0 !important; box-shadow: none !important; }
.tw, .review-table-wrap { display: block !important; width: 100% !important; max-width: 100% !important; min-width: 0 !important; overflow: visible !important; }
table.gt, table.plan { width: 100% !important; max-width: 100% !important; min-width: 0 !important; table-layout: fixed !important; border-collapse: collapse !important; font-size: 7pt !important; }
table.print-wide { font-size: 6pt !important; }
table.print-ultrawide { font-size: 5pt !important; }
table.print-wide .chip, table.print-wide .pill { font-size: 5.5pt !important; padding: 0.2mm 0.7mm !important; letter-spacing: 0 !important; }
table.print-ultrawide .chip, table.print-ultrawide .pill { font-size: 4.5pt !important; padding: 0.1mm 0.4mm !important; letter-spacing: 0 !important; }
table.print-wide .chip.st::before, table.print-ultrawide .chip.st::before { min-width: 0 !important; margin-inline-end: 0.3mm !important; }
table.gt th, table.gt td, table.plan th, table.plan td {
  width: auto !important; max-width: none !important; min-width: 0 !important;
  padding: 1.2mm 1mm !important; line-height: 1.18 !important;
  white-space: normal !important; overflow: visible !important;
  overflow-wrap: anywhere !important; word-break: break-word !important; hyphens: auto;
}
table.gt th, table.plan th { position: static !important; }
thead { display: table-header-group; }
tfoot { display: table-footer-group; }
tr, .card2, .fcard, .actbox, details.pr > summary { break-inside: avoid; page-break-inside: avoid; }
a { overflow-wrap: anywhere; word-break: break-word; }
pre.code { white-space: pre-wrap !important; overflow-wrap: anywhere !important; max-height: none !important; font-size: 6.5pt !important; }
"""

PAGE_POINTS = {
    ("A4", "portrait"): (595.276, 841.89),
    ("A4", "landscape"): (841.89, 595.276),
    ("Letter", "portrait"): (612.0, 792.0),
    ("Letter", "landscape"): (792.0, 612.0),
}


def prepare_html(source: Path, paper_format: str, orientation: str) -> str:
    raw = source.read_text(encoding="utf-8")
    if "Arc Posture Review" not in raw or "<html" not in raw.lower():
        raise ValueError("input is not an Arc Posture Review HTML report")
    soup = BeautifulSoup(raw, "html.parser")
    for details in soup.find_all("details"):
        details["open"] = ""
    for hidden in soup.select("[hidden]"):
        del hidden["hidden"]
    for box in soup.select(".act"):
        classes = list(box.get("class", []))
        if "open" not in classes:
            classes.append("open")
        box["class"] = classes
    for table in soup.find_all("table"):
        max_cols = max((len(row.find_all(["th", "td"], recursive=False)) for row in table.find_all("tr")), default=0)
        classes = list(table.get("class", []))
        if max_cols >= 10 and "print-ultrawide" not in classes:
            classes.append("print-ultrawide")
        elif max_cols >= 8 and "print-wide" not in classes:
            classes.append("print-wide")
        table["class"] = classes
    for script in soup.find_all("script"):
        script.decompose()
    style = soup.new_tag("style")
    style.string = PRINT_CSS.replace("__PAGE_SIZE__", f"{paper_format} {orientation}")
    if not soup.head:
        head = soup.new_tag("head")
        soup.html.insert(0, head)
    soup.head.append(style)
    return str(soup)


def validate_pdf(pdf: Path, source: Path, paper_format: str, orientation: str) -> tuple[int, str]:
    reader = PdfReader(str(pdf))
    if not reader.pages:
        raise ValueError("generated PDF has no pages")
    expected_width, expected_height = PAGE_POINTS[(paper_format, orientation)]
    for index, page in enumerate(reader.pages, 1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if abs(width - expected_width) > 1.0 or abs(height - expected_height) > 1.0:
            raise ValueError(f"page {index} has unexpected size {width:.2f} x {height:.2f} pt")
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    for marker in ("Arc Posture Review", "CHK-01", "CHK-64", "FAIL", "PARTIAL"):
        if marker not in text:
            raise ValueError(f"generated PDF is missing required marker: {marker}")
    forbidden = ["file://", source.resolve().as_uri(), source.name]
    found = [token for token in forbidden if token and token in text]
    if found:
        raise ValueError("browser-style header/footer leaked into PDF: " + ", ".join(found))
    if re.search(r"(?:^|\n)\s*https?://\S+\s*(?:\n|$)", text):
        raise ValueError("standalone URL header/footer detected in PDF text")
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    return len(reader.pages), digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="saved Arc Posture Review HTML")
    parser.add_argument("--output", type=Path, help="PDF output path (default: same stem.pdf)")
    parser.add_argument("--format", choices=("A4", "Letter"), default="A4", dest="paper_format")
    parser.add_argument("--orientation", choices=("portrait", "landscape"), default="landscape")
    args = parser.parse_args()
    source = args.input.resolve()
    if not source.is_file():
        parser.error(f"input not found: {source}")
    output = (args.output or source.with_suffix(".pdf")).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        prepared = prepare_html(source, args.paper_format, args.orientation)
        HTML(string=prepared, base_url=str(source.parent)).write_pdf(str(output))
        pages, digest = validate_pdf(output, source, args.paper_format, args.orientation)
    except Exception as exc:
        print(f"FAIL clean PDF: {exc}")
        return 1
    print(f"PASS clean PDF: {output} · {args.paper_format} {args.orientation} · {pages} page(s) · SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
