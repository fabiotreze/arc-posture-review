#!/usr/bin/env python3
"""Every status shown as a badge in the v4 report must have a color rule."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CP6 = Path(__file__).resolve().parents[1]
REPO = CP6.parents[2]
FIXTURE = REPO / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
CLI = REPO / "assurance" / "v4" / "checkpoint5" / "cli" / "arc_posture.py"
RENDER = CP6 / "report" / "render_v4.py"
NEUTRAL = {"DBA"}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


errors = []
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "assessment.json"
    r = run([sys.executable, str(CLI), "evaluate", "--evidence", str(FIXTURE), "--output", str(out)])
    if r.returncode:
        raise SystemExit("[FAIL] evaluate failed: " + r.stdout + r.stderr)
    for locale in ("en-US", "pt-BR"):
        page = Path(tmp) / ("report." + locale + ".html")
        r = run([sys.executable, str(RENDER), "--input", str(out), "--output", str(page), "--locale", locale])
        if r.returncode:
            errors.append(locale + ": render failed: " + r.stdout + r.stderr)
            continue
        html = page.read_text(encoding="utf-8")
        style = "".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
        if "print-color-adjust" not in style:
            errors.append(locale + ": print-color-adjust is missing")
        classes = set()
        for value in re.findall(r'class="badge ([^"]+)"', html):
            classes.update(value.split())
        missing = []
        for token in sorted(classes):
            if token in NEUTRAL or not re.fullmatch(r"[A-Z_/]{3,}(?::\d+)?", token):
                continue
            prefix = token.split(":")[0]
            if ":" in token:
                ok = ('[class*=" ' + prefix + ':"]') in style
            else:
                escaped = prefix.replace("/", "\\/")
                ok = re.search(r"\.badge\." + re.escape(escaped) + r"(?![A-Za-z0-9_])", style) is not None
            if not ok:
                missing.append(token)
        if missing:
            errors.append("%s: no color rule for: %s" % (locale, ", ".join(missing)))

if errors:
    print("[FAIL] CP6 status colors: %d error(s)" % len(errors))
    for error in errors:
        print(" - " + error)
    raise SystemExit(1)
print("[PASS] CP6 status colors: every status badge has a color rule in en-US and pt-BR")
