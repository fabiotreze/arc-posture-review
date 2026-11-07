#!/usr/bin/env python3
"""Navigation test: every link and jump must resolve and work.

Markdown: internal links, images and anchors of every tracked .md file resolve (no network).
App (EN-US and pt-BR): the five wizard steps switch panes; every guide/checklist jump (data-target) exists and, when
clicked, opens its target in the right pane; the Start-here buttons, the guide search and, after importing the sanitized
package, the verdict/priority jumps and the back button work; the saved analysis has no dangling anchor.
v4 report (EN-US and pt-BR): every side-menu link and CHK link lands on its target; expand/collapse, filters and the
mobile menu work. Saved sample analyses: every anchor resolves.
With --external, every external URL of the Markdown files and of the app pages is requested (needs network; not part of the gate)."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
CLI = ROOT / "assurance/v4/checkpoint5/cli/arc_posture.py"
RENDER = ROOT / "assurance/v4/checkpoint6/report/render_v4.py"
APPS = {"en-US": ROOT / "arc-posture-review.en-US.html", "pt-BR": ROOT / "arc-posture-review.pt-BR.html"}
SAMPLES = {"en-US": ROOT / "docs/examples/sample-analysis.en-US.html", "pt-BR": ROOT / "docs/examples/sample-analysis.pt-BR.html"}
TABS = ["guide", "script", "summary", "result", "report"]
ALLOWED_RELATIVE = {"../../issues"}  # GitHub-relative shortcut, resolved by github.com, not by the file tree

errors: list[str] = []
checked = {"md links": 0, "jumps": 0, "tabs": 0, "report links": 0, "saved anchors": 0}


def fail(message: str) -> None:
    errors.append(message)


# ---------- Markdown ----------
def slug(heading: str) -> str:
    heading = re.sub(r"<[^>]+>", "", heading).strip().lower()
    heading = re.sub(r"[`*_~]", "", heading)
    heading = re.sub(r"[^\w\- ]", "", heading, flags=re.U)
    return heading.replace(" ", "-")


def anchors_of(path: Path, cache: dict[Path, set[str]] = {}) -> set[str]:
    if path in cache:
        return cache[path]
    seen: dict[str, int] = {}
    out: set[str] = set()
    in_code = False
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        match = None if in_code else re.match(r"^#{1,6}\s+(.*)$", line)
        if match:
            base = slug(match.group(1))
            n = seen.get(base, 0)
            seen[base] = n + 1
            out.add(base if n == 0 else f"{base}-{n}")
    out |= set(re.findall(r'<a\s+(?:name|id)="([^"]+)"', text))
    cache[path] = out
    return out


def markdown_files() -> list[Path]:
    # git when the folder is a repository (the gate's isolated copy may not be), otherwise a walk of the tree
    result = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "*.md"], cwd=ROOT, capture_output=True)
    if result.returncode == 0 and result.stdout.strip(b"\0"):
        listed = result.stdout.decode("utf-8").split("\0")
        return [ROOT / p for p in listed if p and (ROOT / p).is_file()]
    ignored = {".git", "build", ".ruff_cache", "__pycache__", "node_modules"}
    return [p for p in ROOT.rglob("*.md") if p.is_file() and not ignored & set(p.relative_to(ROOT).parts)]


LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")


def check_markdown() -> set[str]:
    external: set[str] = set()
    for md in markdown_files():
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8", errors="replace"), flags=re.S)
        for match in list(LINK.finditer(text)) + list(IMAGE.finditer(text)):
            target = match.group(1).strip("<>")
            if target.startswith(("http://", "https://")):
                external.add(target.split("#")[0])
                continue
            if target.startswith(("mailto:", "tel:")) or target in ALLOWED_RELATIVE:
                continue
            checked["md links"] += 1
            path_part, _, fragment = target.partition("#")
            destination = md if not path_part else (md.parent / unquote(path_part)).resolve()
            where = md.relative_to(ROOT).as_posix()
            if path_part and not destination.exists():
                fail(f"{where}: link to a missing file: {target}")
            elif fragment and destination.suffix.lower() == ".md":
                wanted = unquote(fragment)
                if slug(wanted) not in anchors_of(destination) and wanted.lower() not in anchors_of(destination):
                    fail(f"{where}: link to a missing anchor: {target}")
    return external


# ---------- Browser helpers ----------
def new_page(browser, width: int = 1440, height: int = 900) -> tuple[Page, list[str]]:
    page = browser.new_page(viewport={"width": width, "height": height}, reduced_motion="reduce")
    problems: list[str] = []
    page.on("console", lambda m: problems.append(f"console:{m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: problems.append(f"page:{e}"))
    return page, problems


VISIBLE = """(id) => { const e = document.getElementById(id); if (!e) return 'missing';
  const r = e.getBoundingClientRect(), s = getComputedStyle(e);
  return (r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none') ? 'ok' : 'hidden'; }"""


def load_package(page: Page) -> None:
    page.evaluate("var ack = document.querySelector('#privAck'); ack.checked = true; ack.dispatchEvent(new Event('change', {bubbles:true}));")
    page.locator("#zipInput").set_input_files(str(FIXTURE))
    page.wait_for_selector("#btnSaveAna:not([disabled])", state="attached", timeout=120_000)
    page.wait_for_selector("#analysis .qr", state="attached", timeout=120_000)


def active_tab(page: Page) -> str:
    return page.evaluate("() => (document.querySelector('.tab.active') || {dataset: {}}).dataset.tab || ''")


# ---------- App ----------
def check_app(browser, locale: str) -> None:
    label = f"app {locale}"
    page, problems = new_page(browser)
    page.goto(APPS[locale].as_uri(), wait_until="load")

    for name in TABS:  # the five wizard steps
        page.locator(f'.wstep[data-tab="{name}"]').click()
        checked["tabs"] += 1
        active = page.evaluate("() => [...document.querySelectorAll('.pane.active')].map(p => p.id)")
        if active != [f"pane-{name}"] or active_tab(page) != name:
            fail(f"{label}: step '{name}' did not show only its pane (panes {active}, tab {active_tab(page)})")

    targets = page.evaluate("() => [...new Set([...document.querySelectorAll('[data-target]')].map(a => a.dataset.target))]")
    for target in targets:
        if page.evaluate("(t) => !document.getElementById(t)", target):
            if not target.startswith("pr-"):  # priorities exist only after a package is imported
                fail(f"{label}: jump target does not exist: {target}")
            continue
        page.evaluate("(t) => document.querySelector('[data-target=\"' + t + '\"]').click()", target)
        checked["jumps"] += 1
        expected = "script" if target.startswith("item-") else "guide"
        if active_tab(page) != expected:
            fail(f"{label}: jump to {target} opened step '{active_tab(page)}' instead of '{expected}'")
        elif page.evaluate(VISIBLE, target) != "ok":
            fail(f"{label}: jump to {target} left the target not visible")

    count = page.evaluate("() => document.querySelectorAll('[data-goto]').length")
    for index in range(count):  # Start-here and "load the .zip" buttons
        step = page.evaluate("(i) => { const b = document.querySelectorAll('[data-goto]')[i]; b.click(); return b.dataset.goto; }", index)
        checked["tabs"] += 1
        if active_tab(page) != step:
            fail(f"{label}: button #{index} for '{step}' opened '{active_tab(page)}'")

    page.locator('.wstep[data-tab="guide"]').click()
    search = page.locator("#uxGuideSearch")
    if search.count():
        search.fill("CHK-23")
        shown = page.evaluate("() => [...document.querySelectorAll('.guide .act.gf3')].filter(s => s.style.display !== 'none').length")
        total = page.evaluate("() => document.querySelectorAll('.guide .act.gf3').length")
        if not 0 < shown < total:
            fail(f"{label}: guide search for CHK-23 shows {shown} of {total} sections")
        search.fill("")

    load_package(page)  # analysis navigation
    page.locator('.wstep[data-tab="result"]').click()
    pr_targets = page.evaluate("() => [...new Set([...document.querySelectorAll('#analysis [data-target]')].map(a => a.dataset.target))]")
    for target in pr_targets:
        if page.evaluate("(t) => !document.getElementById(t)", target):
            fail(f"{label}: analysis jump target does not exist: {target}")
            continue
        page.locator('.wstep[data-tab="result"]').click()
        page.evaluate("(t) => document.querySelector('#analysis [data-target=\"' + t + '\"]').click()", target)
        checked["jumps"] += 1
        if target.startswith("pr-") and not page.evaluate("(t) => document.getElementById(t).open", target):
            fail(f"{label}: priority {target} was not opened by its jump")
    first = page.locator("#analysis .uxdoc").first
    if first.count():
        page.locator('.wstep[data-tab="result"]').click()
        first.click()
        if not page.evaluate("() => !!document.querySelector('#analysis details.pr[open]')"):
            fail(f"{label}: the first 'do first' card did not open its priority")
    outside = page.locator('#analysis [data-target^="item-"], #analysis [data-target^="g-"]').first
    if outside.count():
        page.locator('.wstep[data-tab="result"]').click()
        page.evaluate("() => (document.querySelector('#analysis [data-target^=\"item-\"], #analysis [data-target^=\"g-\"]')).click()")
        if page.locator("#backAna").is_hidden():
            fail(f"{label}: the back-to-analysis button did not appear after a jump out of the analysis")
        else:
            page.locator("#backAna").click()
            if active_tab(page) != "result":
                fail(f"{label}: the back-to-analysis button did not return to the analysis")

    with page.expect_download(timeout=120_000) as info:  # saved analysis: no dangling anchor
        page.locator("#btnSaveAna").click()
    with tempfile.TemporaryDirectory(prefix="arc-nav-") as temp:
        saved = Path(temp) / info.value.suggested_filename
        info.value.save_as(str(saved))
        check_saved(browser, saved, f"{label} saved analysis", guide_must_exist=False)
    if problems:
        fail(f"{label}: browser errors: {problems[:3]}")
    page.close()


def check_saved(browser, path: Path, label: str, guide_must_exist: bool) -> None:
    page, problems = new_page(browser)
    page.goto(path.resolve().as_uri(), wait_until="load")
    hrefs = page.evaluate("() => [...new Set([...document.querySelectorAll('a[href^=\"#\"]')].map(a => a.getAttribute('href').slice(1)))]")
    for fragment in hrefs:
        checked["saved anchors"] += 1
        if page.evaluate("(f) => !document.getElementById(f)", fragment):
            fail(f"{label}: anchor #{fragment} has no target")
    if page.locator("[data-target]").count():
        fail(f"{label}: unresolved data-target remains in the saved file")
    guide = page.locator(".official-guide-access a")
    if guide.count() != 1:
        fail(f"{label}: the guide access link is missing")
    elif guide_must_exist:
        href = guide.get_attribute("href") or ""
        if not (path.parent / unquote(href.split("#")[0])).resolve().exists():
            fail(f"{label}: the guide link {href} does not resolve from {path.parent.name}/")
    if problems:
        fail(f"{label}: browser errors: {problems[:3]}")
    page.close()


# ---------- v4 report ----------
def check_report(browser, html: Path, locale: str) -> None:
    label = f"v4 report {locale}"
    page, problems = new_page(browser)
    page.goto(html.as_uri(), wait_until="load")
    nav = page.evaluate("() => [...document.querySelectorAll('.side nav a[href^=\"#\"]')].map(a => a.getAttribute('href').slice(1))")
    if len(nav) < 10:
        fail(f"{label}: side menu has only {len(nav)} links")
    for fragment in nav:
        checked["report links"] += 1
        if page.evaluate("(f) => !document.getElementById(f)", fragment):
            fail(f"{label}: menu link #{fragment} has no section")
            continue
        page.locator(f'.side nav a[href="#{fragment}"]').click()
        top = page.evaluate("(f) => Math.round(document.getElementById(f).getBoundingClientRect().top)", fragment)
        if not -4 <= top <= 140:
            fail(f"{label}: menu link #{fragment} landed {top}px from the top")
        if page.evaluate("() => location.hash") != f"#{fragment}":
            fail(f"{label}: menu link #{fragment} did not set the address")
    others = page.evaluate("() => [...new Set([...document.querySelectorAll('a[href^=\"#\"]')].map(a => a.getAttribute('href').slice(1)))]")
    for fragment in others:
        if page.evaluate("(f) => !document.getElementById(f)", fragment):
            fail(f"{label}: link #{fragment} has no target")
    chk = [f for f in others if f.startswith("chk-")]
    if len(chk) < 20:
        fail(f"{label}: only {len(chk)} CHK links found")
    for fragment in chk:
        checked["report links"] += 1
        page.evaluate("(f) => document.querySelector('a[href=\"#' + f + '\"]').click()", fragment)
        if page.evaluate("() => location.hash") != f"#{fragment}":
            fail(f"{label}: CHK link #{fragment} did not set the address")
    page.evaluate("() => scrollTo(0, 0)")
    page.locator("#expand").click()
    if page.evaluate("() => document.querySelectorAll('details:not([open])').length") != 0:
        fail(f"{label}: expand all left blocks closed")
    page.locator("#collapse").click()
    if page.evaluate("() => document.querySelectorAll('details[open]').length") != 0:
        fail(f"{label}: collapse all left blocks open")
    page.evaluate("() => document.getElementById('checks').scrollIntoView()")
    total = page.evaluate("() => document.querySelectorAll('#checks tbody tr').length")
    for chip in page.evaluate("() => [...document.querySelectorAll('[data-filter]')].map(c => c.dataset.filter)"):
        page.locator(f'[data-filter="{chip}"]').click()
        shown = page.evaluate("() => document.querySelectorAll('#checks tbody tr:not([hidden])').length")
        counted = int(page.evaluate("() => (document.getElementById('chkcount') || {textContent: '-1'}).textContent"))
        if shown != counted or (chip == "ALL" and shown != total):
            fail(f"{label}: filter {chip} shows {shown} rows but reports {counted} (total {total})")
    page.locator('[data-filter="ALL"]').click()
    page.locator("#chkfilter").fill("CHK-23")
    if not 0 < page.evaluate("() => document.querySelectorAll('#checks tbody tr:not([hidden])').length") < total:
        fail(f"{label}: the text filter did not narrow the checks")
    page.locator("#chkfilter").fill("")
    page.mouse.wheel(0, 3000)
    page.wait_for_timeout(200)
    if not page.evaluate("() => document.getElementById('totop').classList.contains('show')"):
        fail(f"{label}: back-to-top did not appear after scrolling")
    if problems:
        fail(f"{label}: browser errors: {problems[:3]}")
    page.close()

    mobile, _ = new_page(browser, 390, 844)
    mobile.goto(html.as_uri(), wait_until="load")
    mobile.locator("#navtoggle").click()
    if not mobile.evaluate("() => document.body.classList.contains('navopen')"):
        fail(f"{label}: the mobile menu did not open")
    mobile.locator('.side nav a[href="#checks"]').click()
    if mobile.evaluate("() => document.body.classList.contains('navopen')"):
        fail(f"{label}: the mobile menu stayed open after choosing a section")
    mobile.close()


# ---------- External URLs (optional) ----------
def check_external(urls: set[str]) -> None:
    import ssl
    from concurrent.futures import ThreadPoolExecutor
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
    context = ssl.create_default_context()

    def probe(url: str) -> tuple[str, str]:
        last = "unreachable"
        for method in ("HEAD", "GET"):
            try:
                with urlopen(Request(url, method=method, headers={"User-Agent": "Mozilla/5.0 (link check, read-only)"}), timeout=25, context=context) as response:
                    return url, "ok" if response.status < 400 else str(response.status)
            except HTTPError as exc:
                last = str(exc.code)
                if exc.code in (401, 403, 429):
                    return url, "unverified"
            except (URLError, TimeoutError, OSError) as exc:
                last = f"error {str(exc)[:60]}"
        return url, last

    with ThreadPoolExecutor(max_workers=8) as pool:
        for url, status in pool.map(probe, sorted(urls)):
            if status not in ("ok", "unverified"):
                fail(f"external URL {status}: {url}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--external", action="store_true", help="also request every external URL (needs network)")
    args = parser.parse_args()

    external = check_markdown()
    for locale, app in APPS.items():
        external |= set(re.findall(r'href="(https?://[^"#]+)', app.read_text(encoding="utf-8")))

    launch = {"headless": True}
    if os.environ.get("ARC_REVIEW_BROWSER"):
        launch["executable_path"] = os.environ["ARC_REVIEW_BROWSER"]
    with tempfile.TemporaryDirectory(prefix="arc-nav-report-") as temp, sync_playwright() as playwright:
        assessment = Path(temp) / "assessment.v4.json"
        subprocess.run([sys.executable, str(CLI), "evaluate", "--evidence", str(FIXTURE), "--output", str(assessment)], check=True, capture_output=True)
        browser = playwright.chromium.launch(**launch)
        for locale in APPS:
            check_app(browser, locale)
            report = Path(temp) / f"report.{locale}.html"
            subprocess.run([sys.executable, str(RENDER), "--input", str(assessment), "--locale", locale, "--output", str(report)], check=True, capture_output=True)
            check_report(browser, report, locale)
            check_saved(browser, SAMPLES[locale], f"sample {locale}", guide_must_exist=True)
        browser.close()
    if args.external:
        check_external(external)
    if errors:
        print(f"[FAIL] navigation: {len(errors)} problem(s)")
        for line in errors[:60]:
            print(" - " + line)
        return 1
    scope = ", ".join(f"{n} {k}" for k, n in checked.items()) + (f", {len(external)} external URLs" if args.external else "")
    print(f"[PASS] navigation: {scope} resolve and work (EN-US and pt-BR)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
