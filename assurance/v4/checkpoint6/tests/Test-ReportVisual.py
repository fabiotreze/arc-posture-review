#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader

VIEWPORTS = ((1440, 900), (390, 844))


def open_page(browser, path: Path, width: int, height: int):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors: list[str] = []
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(path.resolve().as_uri(), wait_until="load")
    return page, errors


def verify(browser, path: Path, artifacts: Path, prefix: str) -> None:
    for width, height in VIEWPORTS:
        page, errors = open_page(browser, path, width, height)
        dims = page.evaluate("() => ({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})")
        if errors:
            raise AssertionError(f"{path.name}@{width}: browser errors: {errors[:4]}")
        if dims["scroll"] > dims["client"]:
            raise AssertionError(f"{path.name}@{width}: horizontal overflow")
        if page.locator("section.section").count() != 11:
            raise AssertionError(f"{path.name}: expected 11 report sections")
        if page.locator("[data-scenario-id]").count() != 11:
            raise AssertionError(f"{path.name}: expected 11 scenarios")
        if page.locator("#comparison-null").count() != 1:
            raise AssertionError(f"{path.name}: null comparison disclosure missing")
        if width == 1440:
            page.locator("#collapse").click()
            if page.locator("details[open]").count() != 0:
                raise AssertionError(f"{path.name}: collapse-all failed")
            page.locator("#expand").click()
            if page.locator("details:not([open])").count() != 0:
                raise AssertionError(f"{path.name}: expand-all failed")
        page.screenshot(path=str(artifacts / f"{prefix}-{width}.png"), full_page=False)
        page.close()


def pdf_gate(browser, path: Path, output: Path) -> None:
    page, errors = open_page(browser, path, 1440, 900)
    page.emulate_media(media="print")
    page.pdf(path=str(output), format="A4", landscape=True, print_background=True, display_header_footer=False)
    page.close()
    if errors:
        raise AssertionError(f"{path.name}: PDF browser errors: {errors[:4]}")
    if not output.read_bytes().startswith(b"%PDF") or output.stat().st_size < 20_000:
        raise AssertionError(f"{path.name}: invalid PDF output")
    if len(PdfReader(str(output)).pages) < 1:
        raise AssertionError(f"{path.name}: PDF has no pages")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--en", required=True, type=Path)
    parser.add_argument("--pt", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path)
    args = parser.parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    executable = os.environ.get("ARC_REVIEW_BROWSER")
    launch = {"headless": True}
    if executable:
        launch["executable_path"] = executable
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch)
            verify(browser, args.en, args.artifacts, "v4-en")
            verify(browser, args.pt, args.artifacts, "v4-pt")
            pdf_gate(browser, args.en, args.artifacts / "arc-posture-v4.en-US.pdf")
            pdf_gate(browser, args.pt, args.artifacts / "arc-posture-v4.pt-BR.pdf")
            browser.close()
    except Exception as exc:
        print("[FAIL] Checkpoint 6 Playwright/PDF: " + str(exc))
        return 1
    print("[PASS] Checkpoint 6 Playwright desktop/mobile and clean EN-US/PT-BR PDFs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
