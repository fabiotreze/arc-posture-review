#!/usr/bin/env python3
"""Keyboard and scroll-highlight test, in Chromium, Firefox and WebKit.

App (EN-US and pt-BR): the five wizard steps are reachable with Tab and open with Enter and Space; focus never gets
trapped; every stop shows a visible focus indicator; the privacy box toggles with Space.
v4 report (EN-US and pt-BR): every side-menu link is reachable with Tab and Enter lands on its section; the menu
highlight follows the section in view while scrolling; expand/collapse and the filter chips work with the keyboard;
every stop shows a visible focus indicator."""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
CLI = ROOT / "assurance/v4/checkpoint5/cli/arc_posture.py"
RENDER = ROOT / "assurance/v4/checkpoint6/report/render_v4.py"
APPS = {"en-US": ROOT / "arc-posture-review.en-US.html", "pt-BR": ROOT / "arc-posture-review.pt-BR.html"}
TABS = ["guide", "script", "summary", "result", "report"]
errors: list[str] = []
checked = {"tab stops": 0, "keyboard activations": 0, "highlight checks": 0}

FOCUS = """() => { const e = document.activeElement; if (!e || e === document.body) return null; const s = getComputedStyle(e);
  const ring = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || (s.boxShadow && s.boxShadow !== 'none');
  return {tag: e.tagName, id: e.id || '', href: e.getAttribute('href') || '', ring: !!ring, label: (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 30)}; }"""


def fail(message: str) -> None:
    errors.append(message)


def new_page(browser, width: int = 1440, height: int = 900) -> Page:
    return browser.new_page(viewport={"width": width, "height": height}, reduced_motion="reduce")


def walk_tab_stops(page: Page, label: str, limit: int, key: str = "Tab") -> list[dict]:
    seen: list[dict] = []
    for _ in range(limit):
        page.keyboard.press(key)
        stop = page.evaluate(FOCUS)
        if stop is None:
            break
        checked["tab stops"] += 1
        seen.append(stop)
        if not stop["ring"]:
            fail(f"{label}: no visible focus indicator on {stop['tag']} '{stop['label'] or stop['href'] or stop['id']}'")
    return seen


def check_app(browser, locale: str, name: str) -> None:
    label = f"{name} app {locale}"
    page = new_page(browser)
    page.goto(APPS[locale].as_uri(), wait_until="load")
    stops = walk_tab_stops(page, label, 40, "Tab")
    ids = {(s["tag"], s["label"], s["id"]) for s in stops}
    if len(ids) < 8:
        fail(f"{label}: Tab reached only {len(ids)} distinct stops in 40 presses (keyboard trap?)")
    for step in TABS:
        for key in ("Enter", "Space"):
            page.locator('.wstep[data-tab="guide"]').click()
            page.locator(f'.wstep[data-tab="{step}"]').focus()
            page.keyboard.press(key)
            checked["keyboard activations"] += 1
            active = page.evaluate("() => (document.querySelector('.tab.active') || {dataset: {}}).dataset.tab || ''")
            if active != step:
                fail(f"{label}: {key} on step '{step}' opened '{active}'")
    ack = page.locator("#privAck")
    if ack.count():
        pane = page.evaluate("() => (document.getElementById('privAck').closest('.pane') || {id: ''}).id.replace('pane-', '')")
        page.locator(f'.wstep[data-tab="{pane}"]').click()
        ack.focus()
        before = ack.is_checked()
        page.keyboard.press("Space")
        checked["keyboard activations"] += 1
        if ack.is_checked() == before:
            fail(f"{label}: Space did not toggle the privacy confirmation")
    page.close()


def check_report(browser, report: Path, locale: str, name: str) -> None:
    label = f"{name} v4 report {locale}"
    page = new_page(browser)
    page.goto(report.as_uri(), wait_until="load")
    hrefs = page.evaluate("() => [...document.querySelectorAll('.side nav a[href^=\"#\"]')].map(a => a.getAttribute('href'))")

    # Tab order reaches every menu link; Enter lands on the section.
    page.locator(f'.side nav a[href="{hrefs[0]}"]').focus()
    reached = {hrefs[0]}
    for _ in range(len(hrefs) * 2 + 10):
        page.keyboard.press("Tab")
        stop = page.evaluate(FOCUS)
        if stop is None:
            break
        checked["tab stops"] += 1
        if not stop["ring"]:
            fail(f"{label}: no visible focus indicator on {stop['tag']} '{stop['label'] or stop['href']}'")
        if stop["href"] in hrefs:
            reached.add(stop["href"])
    missing = [h for h in hrefs if h not in reached]
    if missing and name != "webkit":  # Safari/WebKit skips links with Tab by design (Option+Tab or a setting is needed)
        fail(f"{label}: Tab did not reach menu links {missing[:3]}")
    for href in hrefs:
        page.locator(f'.side nav a[href="{href}"]').focus()
        page.keyboard.press("Enter")
        checked["keyboard activations"] += 1
        if page.evaluate("() => location.hash") != href:
            fail(f"{label}: Enter on menu link {href} did not set the address")
            continue
        top = page.evaluate("(h) => Math.round(document.querySelector(h).getBoundingClientRect().top)", href)
        if not -4 <= top <= 140:
            fail(f"{label}: Enter on {href} landed {top}px from the top")

    # The highlighted link follows the section in view while scrolling.
    page.evaluate("() => scrollTo(0, 0)")
    for href in hrefs:
        page.evaluate("(h) => { const e = document.querySelector(h); scrollTo(0, scrollY + e.getBoundingClientRect().top - 90); }", href)
        page.wait_for_timeout(120)
        checked["highlight checks"] += 1
        active = page.evaluate("() => [...document.querySelectorAll('.side nav a.active')].map(a => a.getAttribute('href'))")
        at_end = page.evaluate("() => Math.ceil(scrollY + innerHeight) >= document.documentElement.scrollHeight - 2")
        if active != [href] and not (at_end and len(active) == 1):
            fail(f"{label}: at {href} the highlighted menu links were {active}")

    # Expand/collapse and filter chips with the keyboard.
    page.evaluate("() => scrollTo(0, 0)")
    page.locator("#expand").focus()
    page.keyboard.press("Enter")
    checked["keyboard activations"] += 1
    if page.evaluate("() => document.querySelectorAll('details:not([open])').length") != 0:
        fail(f"{label}: Enter on 'expand all' left blocks closed")
    page.locator("#collapse").focus()
    page.keyboard.press("Space")
    checked["keyboard activations"] += 1
    if page.evaluate("() => document.querySelectorAll('details[open]').length") != 0:
        fail(f"{label}: Space on 'collapse all' left blocks open")
    page.evaluate("() => document.getElementById('checks').scrollIntoView()")
    total = page.evaluate("() => document.querySelectorAll('#checks tbody tr').length")
    chips = page.evaluate("() => [...document.querySelectorAll('[data-filter]')].map(c => c.dataset.filter)")
    for chip in chips:
        page.locator(f'[data-filter="{chip}"]').focus()
        page.keyboard.press("Enter")
        checked["keyboard activations"] += 1
        shown = page.evaluate("() => document.querySelectorAll('#checks tbody tr:not([hidden])').length")
        counted = int(page.evaluate("() => (document.getElementById('chkcount') || {textContent: '-1'}).textContent"))
        if shown != counted or (chip == "ALL" and shown != total):
            fail(f"{label}: Enter on filter {chip} shows {shown} rows but reports {counted} (total {total})")
    page.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--browser", action="append", choices=["chromium", "firefox", "webkit"], help="engine(s) to drive (default: chromium)")
    args = parser.parse_args()
    engines = args.browser or ["chromium"]
    with tempfile.TemporaryDirectory(prefix="arc-key-") as temp, sync_playwright() as playwright:
        assessment = Path(temp) / "assessment.v4.json"
        subprocess.run([sys.executable, str(CLI), "evaluate", "--evidence", str(FIXTURE), "--output", str(assessment)], check=True, capture_output=True)
        reports = {}
        for locale in APPS:
            reports[locale] = Path(temp) / f"report.{locale}.html"
            subprocess.run([sys.executable, str(RENDER), "--input", str(assessment), "--locale", locale, "--output", str(reports[locale])], check=True, capture_output=True)
        for engine in engines:
            browser = getattr(playwright, engine).launch(headless=True)
            for locale in APPS:
                check_app(browser, locale, engine)
                check_report(browser, reports[locale], locale, engine)
            browser.close()
    if errors:
        print(f"[FAIL] keyboard: {len(errors)} problem(s)")
        for line in errors[:60]:
            print(" - " + line)
        return 1
    print("[PASS] keyboard: " + ", ".join(f"{n} {k}" for k, n in checked.items()) + f" in {', '.join(engines)} (EN-US and pt-BR)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
