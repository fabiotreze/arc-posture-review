#!/usr/bin/env python3

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAX = ROOT / "taxonomy" / "v4"

EXPECTED = {
    "zero-trust-principles.json",
    "zero-trust-pillars.json",
    "tiers.json",
    "risk-families.json",
    "attack-surfaces.json",
    "security-boundaries.json",
    "severity.json",
    "assurance.json",
    "control-effectiveness.json",
    "defense-coverage.json",
    "threat-scenarios.json",
    "priority-rules.json",
    "roadmap-policy.json",
    "action-cards.json",
}

errors = []

def load(name):
    path = TAX / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{name}: {exc}")
        return {}

def unique_ids(items, label):
    ids = [x.get("id") for x in items]
    if None in ids:
        errors.append(f"{label}: item without id")
    if len(ids) != len(set(ids)):
        errors.append(f"{label}: duplicate id")
    return set(ids)

actual = {p.name for p in TAX.glob("*.json")}

for name in sorted(EXPECTED - actual):
    errors.append(f"missing taxonomy: {name}")

for name in sorted(actual - EXPECTED):
    errors.append(f"unexpected taxonomy: {name}")

ztp = load("zero-trust-principles.json")
ztpillars = load("zero-trust-pillars.json")
tiers = load("tiers.json")
risks = load("risk-families.json")
surfaces = load("attack-surfaces.json")
boundaries = load("security-boundaries.json")
severity = load("severity.json")
assurance = load("assurance.json")
effectiveness = load("control-effectiveness.json")
defense = load("defense-coverage.json")
threats = load("threat-scenarios.json")
priority = load("priority-rules.json")
roadmap = load("roadmap-policy.json")
cards = load("action-cards.json")

principle_ids = unique_ids(ztp.get("principles", []), "zero trust principles")
pillar_ids = unique_ids(ztpillars.get("pillars", []), "zero trust pillars")
tier_ids = unique_ids(tiers.get("tiers", []), "tiers")
risk_ids = unique_ids(risks.get("riskFamilies", []), "risk families")
surface_ids = unique_ids(surfaces.get("attackSurfaces", []), "attack surfaces")
boundary_ids = unique_ids(boundaries.get("boundaries", []), "security boundaries")
card_ids = unique_ids(cards.get("actionCards", []), "action cards")
scenario_ids = unique_ids(threats.get("stages", []), "threat stages")

if principle_ids != {
    "VERIFY_EXPLICITLY",
    "USE_LEAST_PRIVILEGE",
    "ASSUME_BREACH",
}:
    errors.append("Zero Trust principles must contain exactly the three v4 principles")

if pillar_ids != {"ID", "EP", "DT", "AP", "IN", "NW", "SO"}:
    errors.append("Zero Trust pillars must contain exactly ID/EP/DT/AP/IN/NW/SO")

if not {"T0", "T1", "T2", "GLOBAL", "UNKNOWN"} <= tier_ids:
    errors.append("Tier taxonomy incomplete")

expected_risks = {f"R{i:02d}" for i in range(1, 12)}
if risk_ids != expected_risks:
    errors.append("Risk taxonomy must contain exactly R01-R11")

expected_surfaces = {f"AS{i:02d}" for i in range(1, 12)}
if surface_ids != expected_surfaces:
    errors.append("Attack surface taxonomy must contain exactly AS01-AS11")

if len(boundary_ids) < 7:
    errors.append("Security boundary taxonomy incomplete")

if len(card_ids) != 26:
    errors.append("Action Card taxonomy must contain AC01-AC26")

if scenario_ids != {"TS01", "TS02", "TS03", "TS04", "TS05"}:
    errors.append("Threat scenario lifecycle must contain TS01-TS05")

weights = priority.get("weights", {})
if not math.isclose(sum(weights.values()), 1.0, abs_tol=1e-9):
    errors.append("Priority weights must sum to 1.0")

if priority.get("rules", {}).get("evidenceCoverageChangesRisk") is not False:
    errors.append("Evidence coverage must not directly reduce observed risk")

if priority.get("rules", {}).get("missingEvidenceDefault") != "UNKNOWN":
    errors.append("Missing evidence must default to UNKNOWN")

if priority.get("rules", {}).get("configuredMeansValidated") is not False:
    errors.append("CONFIGURED must not imply VALIDATED")

if priority.get("rules", {}).get("hypothesisMeansAttackPath") is not False:
    errors.append("Hypothesis must not imply attack path")

allowed_priorities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}

for override in priority.get("overrides", []):
    if override.get("minimumPriority") not in allowed_priorities:
        errors.append(
            f"{override.get('id')}: invalid minimumPriority"
        )

for card in cards.get("actionCards", []):
    for risk in card.get("riskFamilies", []):
        if risk not in risk_ids:
            errors.append(
                f"{card.get('id')}: unknown risk family {risk}"
            )

required_defense = {"PREVENT", "DETECT", "RESPOND", "RECOVER"}

if set(defense.get("functions", [])) != required_defense:
    errors.append("Defense coverage must contain Prevent/Detect/Respond/Recover")

if "VALIDATED" not in effectiveness.get("states", []):
    errors.append("Control effectiveness requires VALIDATED state")

if assurance.get("rule", "").lower().find("never reduces") < 0:
    errors.append("Assurance taxonomy must preserve independent risk")

threat_rules = threats.get("rules", [])

if not any("not a validated attack path" in x.lower() for x in threat_rules):
    errors.append("Threat taxonomy must prevent attack-path overstatement")

lane_ids = unique_ids(roadmap.get("lanes", []), "roadmap lanes")

required_lanes = {
    "NOW",
    "DAYS_30",
    "DAYS_90",
    "BACKLOG",
    "DECISION_REQUIRED",
    "ASSURANCE_REQUIRED",
}

if lane_ids != required_lanes:
    errors.append("Roadmap lanes incomplete")

if errors:
    print("FAIL V4 taxonomy")
    for error in errors:
        print(f"  - {error}")
    raise SystemExit(1)

print(
    "PASS V4 taxonomy: "
    f"{len(principle_ids)} Zero Trust principles, "
    f"{len(pillar_ids)} pillars, "
    f"{len(tier_ids)} tier states, "
    f"{len(risk_ids)} risks, "
    f"{len(surface_ids)} attack surfaces, "
    f"{len(card_ids)} Action Cards and "
    f"{len(lane_ids)} roadmap lanes validated"
)
