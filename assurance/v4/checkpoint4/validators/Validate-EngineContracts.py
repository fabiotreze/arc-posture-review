#!/usr/bin/env python3
from validation_lib import *


def main() -> int:
    report = load(); errors = []
    require(report["checkpoint"] == 4 and report["engineVersion"] == "4.0.0-checkpoint4", "engine identity", errors)
    require(report["deterministic"] is True, "deterministic marker", errors)
    require(report["source"]["schemaVersion"] == 3, "collector schema-v3 contract", errors)
    require(report["source"]["integrity"] == "VERIFIED", "reviewed fixture package integrity", errors)
    require(len(report["evidence"]) == len(report["observations"]) == len(report["claims"]) == len(report["controlAssessments"]) == 64, "64-check chain cardinality", errors)
    require(len(report["securityScenarios"]) == 11, "11 Security Scenarios", errors)
    functions = {name for row in report["securityScenarios"] for name in row["defenseAssessment"]}
    require(functions == {"Prevent", "Detect", "Respond", "Recover"}, "defense lifecycle coverage", errors)
    require(report["comparison"] is None, "sample report comparison should be null", errors)
    contracts = set(report["model"]["preservedContracts"])
    for contract in {"collector-schema-v3", "CHK-01..CHK-64", "R01..R11", "AS01..AS11", "missing-evidence-never-PASS", "Control-Result-independent-from-Evidence-Coverage"}:
        require(contract in contracts, f"preserved contract missing: {contract}", errors)
    return finish(errors, "Checkpoint 4 engine contracts")


if __name__ == "__main__":
    raise SystemExit(main())
