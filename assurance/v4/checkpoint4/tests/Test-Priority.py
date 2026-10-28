#!/usr/bin/env python3
from __future__ import annotations

from test_lib import *
from engine.deterministic_engine import horizon_for, priority_for


def main() -> int:
    failures = []
    thresholds = {0: "P3", 34: "P3", 35: "P2", 59: "P2", 60: "P1", 79: "P1", 80: "P0", 100: "P0"}
    for score, expected in thresholds.items():
        if priority_for(score) != expected:
            failures.append(f"priority threshold {score}")
    if any([horizon_for("P0") != "NOW", horizon_for("P1") != "NOW", horizon_for("P2") != "30d", horizon_for("P3") != "90d"]):
        failures.append("horizon mapping")
    evaluator = engine()
    high_t0 = {"severity": "High", "securityScopes": ["T0"]}
    high_t2 = {"severity": "High", "securityScopes": ["T2"]}
    low_t2 = {"severity": "Low", "securityScopes": ["T2"]}
    if evaluator._control_score(high_t0, "REFUTED") <= evaluator._control_score(high_t2, "REFUTED"):
        failures.append("T0 context did not outrank T2")
    if priority_for(evaluator._control_score(high_t0, "REFUTED")) != "P0":
        failures.append("High/T0 conclusive failure is not P0")
    if priority_for(evaluator._control_score(low_t2, "REFUTED")) != "P3":
        failures.append("Low/T2 control priority inflation")
    result = evaluator.evaluate(fixture())
    cards = result["actionCards"]
    ordered = sorted(cards, key=lambda item: ({"P0": 0, "P1": 1, "P2": 2, "P3": 3}[item["priority"]], -item["priorityScore"], item["riskId"]))
    if cards != ordered:
        failures.append("Action Card ordering is not deterministic")
    if failures:
        print(f"[FAIL] priority: {len(failures)} error(s)")
        for item in failures: print(" - " + item)
        return 1
    print("[PASS] priority: thresholds, Tier weighting, stable ordering and NOW/30d/90d horizons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
