#!/usr/bin/env python3
"""The app shows the v4 report packaged by the collector: buttons, no integrity warning for report/, popup and download."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
CLI = ROOT / "assurance/v4/checkpoint5/cli/arc_posture.py"
RENDER = ROOT / "assurance/v4/checkpoint6/report/render_v4.py"


def build_package(tmp: Path) -> Path:
    with zipfile.ZipFile(FIXTURE) as z:
        z.extractall(tmp / "run")
    run_dir = next(p.parent for p in (tmp / "run").rglob("results.json"))
    report = run_dir / "report"
    report.mkdir()
    assessment = report / "assessment.v4.json"
    subprocess.run([sys.executable, str(CLI), "evaluate", "--evidence", str(FIXTURE), "--output", str(assessment)], check=True, capture_output=True)
    for loc in ("en-US", "pt-BR"):
        subprocess.run([sys.executable, str(RENDER), "--input", str(assessment), "--locale", loc, "--output", str(report / f"arc-posture-review.v4.{loc}.html")], check=True, capture_output=True)
    package = tmp / "arc-posture-review-test.zip"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(run_dir.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(run_dir).as_posix())
    return package


errors = []
tmp = Path(tempfile.mkdtemp())
try:
    package = build_package(tmp)
    executable = os.environ.get("ARC_REVIEW_BROWSER")
    launch = {"headless": True, **({"executable_path": executable} if executable else {})}
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch)
        for name, report_marker in (("arc-posture-review.en-US.html", "Executive summary"), ("arc-posture-review.pt-BR.html", "Resumo executivo")):
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto((ROOT / name).as_uri())
            page.evaluate("var ack = document.querySelector('#privAck'); ack.checked = true; ack.dispatchEvent(new Event('change', {bubbles:true}));")
            page.locator("#zipInput").set_input_files(str(package))
            page.wait_for_selector("#btnSaveAna:not([disabled])", state="attached", timeout=60000)
            page.locator('.wstep[data-tab="result"]').click()
            if page.locator("#btnV4Open").get_attribute("hidden") is not None or page.locator("#btnV4Save").get_attribute("hidden") is not None:
                errors.append(f"{name}: v4 buttons are hidden although the package has report/")
                continue
            shown = (page.locator("#summaryOut").text_content() or "") + (page.locator("#analysis").text_content() or "")
            if ("Files outside the manifest" in shown or "Arquivos fora do manifest" in shown):
                errors.append(f"{name}: report/ is flagged as a file outside the manifest")
            with page.expect_popup() as popup_info:
                page.locator("#btnV4Open").click()
            popup = popup_info.value
            popup.wait_for_load_state("load")
            if popup.locator("#executive-narrative").count() != 1 or report_marker not in popup.locator("#executive-narrative").inner_text():
                errors.append(f"{name}: the opened report is not the canonical v4 report in the expected language")
            popup.close()
            with page.expect_download() as download_info:
                page.locator("#btnV4Save").click()
            if not download_info.value.suggested_filename.startswith("arc-posture-review.v4."):
                errors.append(f"{name}: unexpected v4 download name {download_info.value.suggested_filename}")
            page.close()
        # A package without report/ keeps the buttons hidden.
        plain = tmp / "plain.zip"
        with zipfile.ZipFile(package) as src, zipfile.ZipFile(plain, "w", zipfile.ZIP_DEFLATED) as dst:
            for item in src.infolist():
                if not item.filename.startswith("report/"):
                    dst.writestr(item, src.read(item.filename))
        page = browser.new_page()
        page.goto((ROOT / "arc-posture-review.en-US.html").as_uri())
        page.evaluate("var ack = document.querySelector('#privAck'); ack.checked = true; ack.dispatchEvent(new Event('change', {bubbles:true}));")
        page.locator("#zipInput").set_input_files(str(plain))
        page.wait_for_selector("#btnSaveAna:not([disabled])", state="attached", timeout=60000)
        if page.locator("#btnV4Open").get_attribute("hidden") is None:
            errors.append("v4 buttons are visible for a package without report/")
        browser.close()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(("FAIL" if errors else "PASS") + " app v4 report: " + ("; ".join(errors) if errors else
      "buttons appear only when the package carries report/, no manifest warning, the report opens and saves in EN-US and PT-BR"))
sys.exit(1 if errors else 0)
