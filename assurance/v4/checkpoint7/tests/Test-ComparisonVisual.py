#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--screenshot", required=True, type=Path)
    args = parser.parse_args()
    args.screenshot.parent.mkdir(parents=True, exist_ok=True)
    launch = {"headless": True}
    if os.environ.get("ARC_REVIEW_BROWSER"):
        launch["executable_path"] = os.environ["ARC_REVIEW_BROWSER"]
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            errors: list[str] = []
            page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(args.html.resolve().as_uri(), wait_until="load")
            if page.locator("#comparison-null").count():
                raise AssertionError("comparison null disclosure shown for a before/after report")
            verified = page.get_by_text("Verified Improvement", exact=True)
            if verified.count() < 1:
                raise AssertionError("expected at least one Verified Improvement")
            improved_control = page.locator("#comparison tr", has_text="CHK-23").filter(has_text="Verified Improvement")
            if improved_control.count() != 1:
                raise AssertionError("CHK-23 is not presented as the canonical Verified Improvement")
            comparison = page.locator("#comparison")
            text = comparison.inner_text()
            for marker in ("CHK-23", "IMPROVED", "CHK-07", "REGRESSED", "Before score", "After score"):
                if marker not in text:
                    raise AssertionError(f"comparison visual missing {marker}")
            if errors:
                raise AssertionError(f"browser errors: {errors[:4]}")
            comparison.screenshot(path=str(args.screenshot))
            browser.close()
    except Exception as exc:
        print("[FAIL] CP7 before/after visual: " + str(exc))
        return 1
    print("[PASS] CP7 before/after visual and Verified Improvement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
