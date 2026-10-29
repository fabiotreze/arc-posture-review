#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CATALOG = ROOT / "criteria/v4/check-catalog.v4.json"
CSV_MAP = ROOT / "criteria/v4/check-catalog.v4.csv"
SCENARIOS = ROOT / "security-scenarios/v4/scenarios.v4.json"

errors = []

cat = json.loads(CATALOG.read_text(encoding="utf-8"))
sec = json.loads(SCENARIOS.read_text(encoding="utf-8"))

checks = cat["checks"]
scenarios = sec["scenarios"]

ids = [x["id"] for x in checks]
scenario_ids = {x["scenarioId"] for x in scenarios}

required = {f"CHK-{i:02d}" for i in range(1, 65)}

if len(ids) != len(set(ids)):
    errors.append("duplicate CHK IDs")

missing = required - set(ids)
if missing:
    errors.append("missing baseline checks: " + ",".join(sorted(missing)))

if len(checks) < 64:
    errors.append("catalog must contain at least 64 checks")

for check in checks:
    refs = set(check.get("scenarioIds", []))

    if not refs:
        errors.append(f"{check['id']}: no Security Scenario")

    orphan = refs - scenario_ids
    if orphan:
        errors.append(
            f"{check['id']}: invalid scenarios {sorted(orphan)}"
        )

    if check.get("assessmentMode") == "automated" and not check.get("datasets"):
        errors.append(f"{check['id']}: automated check without dataset")

legacy = {"ERRO", "PARCIAL", "MANUAL"}

for check in checks:
    allowed = set(
        check.get("resultContract", {}).get("allowedResults", [])
    )

    bad = allowed & legacy

    if bad:
        errors.append(
            f"{check['id']}: legacy result aliases {sorted(bad)}"
        )

chk32 = next(x for x in checks if x["id"] == "CHK-32")
chk33 = next(x for x in checks if x["id"] == "CHK-33")

title32 = chk32["title"]

if isinstance(title32, dict):
    title32 = title32.get("en-US", "")

if title32 != "MDE extension deployed through Arc":
    errors.append("CHK-32 canonical title drift")

if str(chk33.get("severity", "")).lower() != "high":
    errors.append("CHK-33 severity must be High")

with CSV_MAP.open(encoding="utf-8-sig", newline="") as f:
    csv_rows = list(csv.DictReader(f))

if len(csv_rows) != len(checks):
    errors.append("CSV and JSON catalog counts differ")

csv_ids = {row["id"] for row in csv_rows}

if csv_ids != set(ids):
    errors.append("CSV and JSON IDs differ")

scenario_counts = Counter(
    s
    for check in checks
    for s in check.get("scenarioIds", [])
)

if errors:
    print("FAIL V4 mapping")
    for error in errors:
        print("  -", error)
    raise SystemExit(1)

print(
    f"PASS V4 mapping: {len(checks)} checks, "
    f"{len(scenarios)} Security Scenarios, "
    f"{sum(1 for c in checks if c.get('assessmentMode') == 'automated')} automated, "
    f"{sum(1 for c in checks if c.get('assessmentMode') != 'automated')} documentary"
)

for scenario in sorted(scenario_ids):
    print(f"  {scenario}: {scenario_counts[scenario]} checks")
