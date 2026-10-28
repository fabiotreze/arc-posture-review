#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
CP5 = REPO_ROOT / "assurance" / "v4" / "checkpoint5"
sys.path.insert(0, str(CP5))
from engine.canonical_v4 import digest, validate_canonical_assessment

report = json.loads((CP5 / "reports" / "assessment-result.v4.json").read_text(encoding="utf-8-sig"))
comparison = json.loads((CP5 / "reports" / "assessment-comparison.v4.json").read_text(encoding="utf-8-sig"))
errors = []
try:
    validate_canonical_assessment(report)
except Exception as exc:
    errors.append(str(exc))
expected_controls = {f"CHK-{i:02d}" for i in range(1, 65)}
expected_scenarios = {f"AS{i:02d}" for i in range(1, 12)}
for label, rows in (("Zero Trust", report["zeroTrust"]["controlMappings"]), ("Tiers", report["tiers"]["controlMappings"])):
    if {row["checkId"] for row in rows} != expected_controls: errors.append(f"{label} control coverage")
if {row["scenarioId"] for row in report["defenseCoverage"]["scenarios"]} != expected_scenarios: errors.append("defense scenario coverage")
control_ids = {row["checkId"] for row in report["residualRisk"]["controls"]}
scenario_ids = {row["scenarioId"] for row in report["residualRisk"]["scenarios"]}
if control_ids != expected_controls: errors.append("residual control coverage")
if scenario_ids != expected_scenarios: errors.append("residual scenario coverage")
card_ids = {row["id"] for row in report["actionCards"]}
roadmap_ids = {item["actionCardId"] for horizon in ("NOW", "30d", "90d") for item in report["roadmap"][horizon]}
if card_ids != roadmap_ids: errors.append("Action Card to roadmap conservation")
semantic = dict(report); output_digest = semantic.pop("outputDigest")
if output_digest != digest(semantic): errors.append("assessment outputDigest")
comparison_semantic = dict(comparison); comparison_digest = comparison_semantic.pop("outputDigest")
if comparison_digest != digest(comparison_semantic): errors.append("comparison outputDigest")
if sum(comparison["summary"].values()) != 64: errors.append("comparison control conservation")
if len(comparison["scenarios"]) != 11: errors.append("comparison scenario cardinality")
if errors:
    print(f"[FAIL] Checkpoint 5 semantic contract: {len(errors)} error(s)")
    for error in errors: print(" - " + error)
    raise SystemExit(1)
print("[PASS] Checkpoint 5 semantic contract and cross-section conservation")
