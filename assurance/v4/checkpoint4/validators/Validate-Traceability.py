#!/usr/bin/env python3
from validation_lib import *


def main() -> int:
    report = load(); errors = []
    evidence = {row["checkId"]: row for row in report["evidence"]}
    observations = {row["checkId"]: row for row in report["observations"]}
    claims = {row["checkId"]: row for row in report["claims"]}
    controls = {row["checkId"]: row for row in report["controlAssessments"]}
    expected = {f"CHK-{i:02d}" for i in range(1, 65)}
    for label, rows in [("evidence", evidence), ("observations", observations), ("claims", claims), ("controls", controls)]:
        require(set(rows) == expected, f"{label}: CHK key drift", errors)
    cp3_checks = {row["id"]: row for row in cp3("checks.enriched.json")}
    for check_id in sorted(expected):
        ev, ob, cl, ce = evidence[check_id], observations[check_id], claims[check_id], controls[check_id]
        require(ob["evidenceId"] == ev["id"], f"{check_id}: Evidence -> Observation trace", errors)
        require(cl["observationId"] == ob["id"], f"{check_id}: Observation -> Claim trace", errors)
        require(ce["trace"] == [ev["id"], ob["id"], cl["id"]], f"{check_id}: control trace", errors)
        require(ce["claimId"] == cl["id"], f"{check_id}: Claim -> Control trace", errors)
        model = cp3_checks[check_id]
        for field in ("securityModelStage", "securityScopes", "riskIds", "scenarioIds", "securityBoundaryIds", "defenseFunctions", "mappingConfidence"):
            require(ce[field] == model[field], f"{check_id}: Checkpoint 3 mapping drift in {field}", errors)
        if cl["verdict"] == "SUPPORTED":
            require(ev["coverage"] == "FULL" and not ev["missingFields"], f"{check_id}: unsupported PASS escaped evidence gate", errors)
        if ob["status"] == "N/A" and cl["verdict"] == "NOT_APPLICABLE":
            require(ev["coverage"] == "FULL" and not ev["missingFields"], f"{check_id}: unsupported N/A escaped applicability gate", errors)
    scenarios = {row["scenarioId"]: row for row in report["securityScenarios"]}
    for static in cp3("security-scenarios.json"):
        row = scenarios[static["id"]]
        require(row["controlIds"] == sorted(static["controlCheckIds"]), f"{static['id']}: control mapping drift", errors)
        require(row["attackConfirmation"] == "NOT_ASSERTED", f"{static['id']}: compromise/exploitation overclaim", errors)
        require(set(row["triggeredControlIds"]) <= set(row["controlIds"]), f"{static['id']}: trigger outside scenario", errors)
    unsigned = {key: value for key, value in report.items() if key != "outputDigest"}
    require(report["outputDigest"] == digest(unsigned), "outputDigest mismatch", errors)
    return finish(errors, "Evidence -> Observation -> Claim -> Control -> Scenario traceability")


if __name__ == "__main__":
    raise SystemExit(main())
