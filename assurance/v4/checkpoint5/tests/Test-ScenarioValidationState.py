#!/usr/bin/env python3
"""CP5.2: scenario validationState must never overstate the evidence."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CP5 = Path(__file__).resolve().parents[1]
REPO = CP5.parents[2]
FIXTURE = REPO / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
CATALOG = REPO / "assurance" / "v4" / "checkpoint3" / "data" / "security-scenarios.json"
ALLOWED = {"HYPOTHESIS", "POTENTIAL_RELEVANCE"}

errors = []
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "result.json"
    run = subprocess.run(
        [sys.executable, str(CP5 / "cli" / "arc_posture.py"), "evaluate",
         "--evidence", str(FIXTURE), "--output", str(out)],
        capture_output=True, text=True,
    )
    if run.returncode:
        raise SystemExit("[FAIL] evaluate failed: " + run.stdout + run.stderr)
    doc = json.loads(out.read_text(encoding="utf-8"))

catalog = json.loads(CATALOG.read_text(encoding="utf-8-sig"))
rows = catalog if isinstance(catalog, list) else next(v for v in catalog.values() if isinstance(v, list))
by_id = {row["id"]: row for row in rows}

for scenario in doc["securityScenarios"]:
    sid = scenario["scenarioId"]
    state = scenario.get("validationState")
    if state not in ALLOWED:
        errors.append("%s: validationState %r is stronger than the evidence supports" % (sid, state))
    expected = (
        "POTENTIAL_RELEVANCE"
        if scenario["attackPathAssessment"] in ("EXPOSURE_INDICATED", "WEAKNESS_INDICATED")
        else "HYPOTHESIS"
    )
    if state != expected:
        errors.append("%s: validationState %r does not follow the rule (%r)" % (sid, state, expected))
    if scenario["attackConfirmation"] != "NOT_ASSERTED":
        errors.append("%s: attackConfirmation must stay NOT_ASSERTED" % sid)
    if [edge["from"] for edge in scenario["attackPath"]] != ["IDENTITY", "MANAGEMENT", "HOST"]:
        errors.append("%s: attackPath is not IDENTITY -> MANAGEMENT -> HOST" % sid)
    if scenario["attackPath"] != by_id[sid]["attackPath"] or scenario["hypothesis"] != by_id[sid]["hypothesis"]:
        errors.append("%s: attackPath or hypothesis differs from the CP3 catalog" % sid)

if errors:
    print("[FAIL] CP5.2 scenario validationState: %d error(s)" % len(errors))
    for error in errors:
        print(" - " + error)
    raise SystemExit(1)
print(
    "[PASS] CP5.2 scenario validationState: %d scenarios, none above POTENTIAL_RELEVANCE, "
    "catalog copied unchanged" % len(doc["securityScenarios"])
)
