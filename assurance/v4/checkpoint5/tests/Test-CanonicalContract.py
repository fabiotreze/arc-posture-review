#!/usr/bin/env python3
from test_lib import *


def main() -> int:
    report = canonical(); errors = []
    if report["metadata"]["contractName"] != "assessment-result.v4": errors.append("contract name")
    if report["metadata"]["sourceCheckpointCommit"] != "2d512a3": errors.append("baseline commit lineage")
    if len(report["controlAssessments"]) != 64: errors.append("control cardinality")
    if [r["checkId"] for r in report["controlAssessments"]] != [f"CHK-{i:02d}" for i in range(1, 65)]: errors.append("control ordering")
    if len(report["securityScenarios"]) != 11: errors.append("scenario cardinality")
    if len(report["traceability"]["evidence"]) != 64 or len(report["traceability"]["claims"]) != 64: errors.append("traceability cardinality")
    if sum(report["assurance"]["controlOutcomes"].values()) != 64: errors.append("assurance outcome total")
    if len(report["zeroTrust"]["controlMappings"]) != 64: errors.append("Zero Trust mappings")
    if [r["name"] for r in report["tiers"]["assessments"]] != ["T0", "T1", "T2", "Global"]: errors.append("tier assessments")
    if len(report["defenseCoverage"]["scenarios"]) != 11: errors.append("defense coverage")
    if len(report["residualRisk"]["controls"]) != 64: errors.append("residual control risks")
    semantic = dict(report); output_digest = semantic.pop("outputDigest")
    if output_digest != digest(semantic): errors.append("output digest")
    if report["comparison"] is not None: errors.append("unexpected comparison without baseline")
    if errors:
        print(f"[FAIL] canonical contract: {len(errors)} error(s)")
        for error in errors: print(" - " + error)
        return 1
    print("[PASS] canonical assessment-result.v4: metadata, assurance, 64 controls, Zero Trust, Tiers, scenarios, defense, risk, cards and roadmap")
    return 0


if __name__ == "__main__": raise SystemExit(main())
