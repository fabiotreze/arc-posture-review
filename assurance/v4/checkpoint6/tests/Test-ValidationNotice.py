#!/usr/bin/env python3
"""The v4 report must carry the validation notice in both locales."""
import subprocess
import sys
import tempfile
from pathlib import Path

CP6 = Path(__file__).resolve().parents[1]
REPO = CP6.parents[2]
FIXTURE = REPO / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
CLI = REPO / "assurance" / "v4" / "checkpoint5" / "cli" / "arc_posture.py"
RENDER = CP6 / "report" / "render_v4.py"
EXPECTED = {
    "en-US": ("absolute truth", "validated and certified", "DISCLAIMER.md"),
    "pt-BR": ("verdade absoluta", "validado e certificado", "DISCLAIMER.md"),
}

errors = []
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "assessment.json"
    run = subprocess.run(
        [sys.executable, str(CLI), "evaluate", "--evidence", str(FIXTURE), "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if run.returncode:
        raise SystemExit("[FAIL] evaluate failed: " + run.stdout + run.stderr)
    for locale, phrases in EXPECTED.items():
        html_path = Path(tmp) / ("report." + locale + ".html")
        render = subprocess.run(
            [sys.executable, str(RENDER), "--input", str(out), "--output", str(html_path), "--locale", locale],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if render.returncode:
            errors.append(locale + ": render failed: " + render.stdout + render.stderr)
            continue
        html = html_path.read_text(encoding="utf-8")
        if 'id="validation-notice"' not in html:
            errors.append(locale + ": validation notice is missing")
        if "{notice_html}" in html:
            errors.append(locale + ": validation notice was not interpolated")
        for phrase in phrases:
            if phrase not in html:
                errors.append("%s: missing phrase %r" % (locale, phrase))

if errors:
    print("[FAIL] CP6 validation notice: %d error(s)" % len(errors))
    for error in errors:
        print(" - " + error)
    raise SystemExit(1)
print("[PASS] CP6 validation notice present in en-US and pt-BR")
