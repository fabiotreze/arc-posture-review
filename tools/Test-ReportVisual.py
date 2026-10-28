#!/usr/bin/env python3
"""Playwright regression tests for the app and generated/saved reports."""
from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
VIEWPORTS = [(1440, 900), (390, 844)]


def assert_page_clean(page: Page, label: str, errors: list[str]) -> None:
    if errors:
        raise AssertionError(f"{label}: browser errors: {errors[:5]}")
    dims = page.evaluate("() => ({scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth})")
    if dims["scroll"] > dims["client"]:
        raise AssertionError(f"{label}: horizontal overflow {dims['scroll']} > {dims['client']}")


def open_page(browser, path: Path, width: int, height: int):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors: list[str] = []
    page.on("console", lambda message: errors.append(f"console:{message.text}") if message.type == "error" else None)
    page.on("pageerror", lambda error: errors.append(f"page:{error}"))
    page.goto(path.resolve().as_uri(), wait_until="load")
    return page, errors


def test_saved_report(browser, path: Path, artifacts: Path | None, prefix: str) -> None:
    for width, height in VIEWPORTS:
        page, errors = open_page(browser, path, width, height)
        assert_page_clean(page, f"{path.name}@{width}", errors)
        if page.locator("button.copyk").count() == 0:
            raise AssertionError(f"{path.name}: no query copy buttons")
        guide = page.locator(".official-guide-access a")
        if guide.count() != 1 or not guide.get_attribute("href").endswith(".html"):
            raise AssertionError(f"{path.name}: explicit Guide HTML link missing")
        if page.locator('a[download$=".md"], a[href$=".md"]').count() != 0:
            raise AssertionError(f"{path.name}: Markdown download link was reintroduced")
        if width == 1440:
            button = page.locator("button.copyk").first
            original = button.inner_text()
            button.click()
            page.wait_for_timeout(100)
            if button.inner_text() not in {"Copied", "Copiado"}:
                raise AssertionError(f"{path.name}: offline query copy did not report success")
            page.wait_for_timeout(1700)
            if button.inner_text() != original:
                raise AssertionError(f"{path.name}: copy-button label was not restored")
            initially_closed = page.locator("details:not([open])").count()
            page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
            if page.locator("details:not([open])").count() != 0:
                raise AssertionError(f"{path.name}: beforeprint did not expand every details block")
            page.evaluate("window.dispatchEvent(new Event('afterprint'))")
            if page.locator("details:not([open])").count() != initially_closed:
                raise AssertionError(f"{path.name}: afterprint did not restore details state")
            if page.locator("#analysis .act:not(.open)").count() != 0:
                raise AssertionError(f"{path.name}: exported alert/report sections are not visually open")
        if artifacts:
            page.screenshot(path=str(artifacts / f"{prefix}-{width}.png"), full_page=False)
        page.close()


def test_app(browser, path: Path, artifacts: Path | None, prefix: str) -> None:
    for width, height in VIEWPORTS:
        page, errors = open_page(browser, path, width, height)
        assert_page_clean(page, f"{path.name}@{width}", errors)
        if page.locator(".wiz .wstep").count() != 5:
            raise AssertionError(f"{path.name}: wizard does not expose five steps")
        if page.locator("#btnGuideMd, #mdSource").count() != 0:
            raise AssertionError(f"{path.name}: retired Markdown guide surface is visible or embedded")
        if "v3.9.5" not in page.locator("#verBadge").inner_text():
            raise AssertionError(f"{path.name}: runtime version badge mismatch")
        if artifacts:
            page.screenshot(path=str(artifacts / f"{prefix}-{width}.png"), full_page=False)
        page.close()


def test_end_to_end(browser, app: Path, package: Path, artifacts: Path | None, locale: str) -> None:
    page, errors = open_page(browser, app, 1440, 900)
    page.evaluate("var ack = document.querySelector('#privAck'); ack.checked = true; ack.dispatchEvent(new Event('change', {bubbles:true}));")
    page.locator("#zipInput").set_input_files(str(package.resolve()))
    page.wait_for_selector("#btnSaveAna:not([disabled])", state="attached", timeout=120_000)
    page.wait_for_selector("#analysis .qr", state="attached", timeout=120_000)
    page.locator('.wstep[data-tab="result"]').click()
    if page.locator("#analysis details.pr").count() == 0:
        raise AssertionError("end-to-end: imported package produced no priorities")
    if page.locator("#analysis details.pr .actbox").count() != page.locator("#analysis details.pr").count():
        raise AssertionError("end-to-end: action guidance is missing or duplicated")
    coverage = "Assessment Coverage" if locale == "en-US" else "Cobertura da avaliação"
    evidence = "Evidence contract by check" if locale == "en-US" else "Contrato de evidência por verificação"
    rounding = "Score before rounding" if locale == "en-US" else "Nota antes do arredondamento"
    executive = "Executive assessment" if locale == "en-US" else "Avaliação executiva"
    appendix = "Evidence appendix" if locale == "en-US" else "Apêndice de evidências"
    for label, message in [(coverage, "coverage"), (evidence, "evidence contract"), (rounding, "score trace"), (executive, "executive assessment"), (appendix, "evidence appendix")]:
        if page.get_by_text(label, exact=False).count() == 0:
            raise AssertionError(f"end-to-end {locale}: missing {message}")
    rounding_note = "displayed values are rounded" if locale == "en-US" else "valores exibidos arredondados"
    if page.get_by_text(rounding_note, exact=False).count() == 0:
        raise AssertionError(f"end-to-end {locale}: rounded-value disclosure is missing")
    if page.locator("#analysis table.print-ultrawide").count() == 0:
        raise AssertionError(f"end-to-end {locale}: print width classes were not rendered")
    if page.locator("#analysis .st-PARTIAL").count() == 0:
        raise AssertionError("end-to-end: reviewed PARTIAL results are not rendered")
    if page.locator("#analysis .st-ERRO, #analysis .st-PARCIAL").count() != 0:
        raise AssertionError("end-to-end: legacy status classes were rendered")
    expected_cardinality = "5 finding(s)" if locale == "en-US" else "5 achado(s)"
    if expected_cardinality not in page.locator("#pr-CHK-55 summary").inner_text():
        raise AssertionError("end-to-end: CHK-55 cardinality is not five affected machines")
    page.locator("#pr-CHK-33").evaluate("element => { element.open = true; element.dispatchEvent(new Event('toggle')); }")
    page.wait_for_selector("#pr-CHK-33 a.full-evidence", state="attached", timeout=120_000)
    preview = "Preview: 10 of 228" if locale == "en-US" else "Prévia: 10 de 228"
    if preview not in page.locator("#pr-CHK-33 details.items summary").inner_text():
        raise AssertionError("end-to-end: CHK-33 preview boundary is missing")
    full = "228 rows" if locale == "en-US" else "228 linhas"
    if full not in page.locator("#pr-CHK-33 a.full-evidence").inner_text():
        raise AssertionError("end-to-end: complete CHK-33 evidence link is missing")
    if locale == "pt-BR":
        visible = page.locator("#analysis").inner_text()
        for untranslated in ["Executive assessment", "Evidence appendix", "Assessment Coverage", "Evidence contract by check", "High confidence", "Medium confidence", "Low confidence", "One vault has a definite baseline gap", "228 Defender recommendations affect Arc machines", "Sentinel exists in the collected scope", "Canonical patch evidence: exactly one row", "Four SQL extensions have conclusive technical failures", "Evidence Coverage is PARTIAL", "Collector dataset(s); CLI calls and failures are recorded"]:
            if untranslated in visible:
                raise AssertionError(f"end-to-end pt-BR: untranslated renderer text: {untranslated}")
    assert_page_clean(page, "end-to-end application", errors)
    with page.expect_download(timeout=120_000) as info:
        page.locator("#btnSaveAna").click()
    download = info.value
    with tempfile.TemporaryDirectory(prefix="arc-review-e2e-") as temp:
        saved = Path(temp) / download.suggested_filename
        download.save_as(str(saved))
        if not saved.exists() or saved.stat().st_size < 50_000:
            raise AssertionError("end-to-end: generated report was not downloaded correctly")
        if artifacts:
            exported = artifacts / f"e2e-{locale}.html"
            exported.write_bytes(saved.read_bytes())
        test_saved_report(browser, saved, artifacts, f"e2e-saved-{locale}")
    page.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, help="optional evidence ZIP for full import/export validation")
    parser.add_argument("--artifacts", type=Path, help="optional screenshot output directory")
    args = parser.parse_args()
    if args.package and not args.package.exists():
        parser.error(f"package not found: {args.package}")
    if args.artifacts:
        args.artifacts.mkdir(parents=True, exist_ok=True)

    executable = os.environ.get("ARC_REVIEW_BROWSER")
    launch = {"headless": True}
    if executable:
        launch["executable_path"] = executable
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch)
            test_app(browser, ROOT / "arc-posture-review.en-US.html", args.artifacts, "app-en")
            test_app(browser, ROOT / "arc-posture-review.pt-BR.html", args.artifacts, "app-pt")
            test_saved_report(browser, ROOT / "docs/examples/sample-analysis.en-US.html", args.artifacts, "sample-en")
            test_saved_report(browser, ROOT / "docs/examples/sample-analysis.pt-BR.html", args.artifacts, "sample-pt")
            if args.package:
                test_end_to_end(browser, ROOT / "arc-posture-review.en-US.html", args.package, args.artifacts, "en-US")
                test_end_to_end(browser, ROOT / "arc-posture-review.pt-BR.html", args.package, args.artifacts, "pt-BR")
            browser.close()
    except Exception as exc:
        print("FAIL", exc)
        return 1
    scope = " + package import/export" if args.package else ""
    print("PASS Playwright: desktop/mobile layout, CSP, copy, print and app" + scope)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
