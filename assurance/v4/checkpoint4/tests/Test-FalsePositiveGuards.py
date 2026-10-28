#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

from test_lib import *
from engine.deterministic_engine import EvaluationError, load_evidence


def main() -> int:
    failures = []
    base = fixture(); evaluator = engine()

    pass_without_evidence = mutated(base, lambda d: row(d, "CHK-07").update(status="PASS", evidenceCoverage="NONE"))
    result = evaluator.evaluate(pass_without_evidence)
    if claim(result, "CHK-07")["verdict"] != "UNRESOLVED" or control(result, "CHK-07")["outcome"] != "UNASSESSED":
        failures.append("PASS without full evidence was not suppressed")
    if "PASS_WITHOUT_FULL_EVIDENCE" not in observation(result, "CHK-07")["falsePositiveGuards"]:
        failures.append("PASS suppression was not traceable")

    na_without_evidence = mutated(base, lambda d: row(d, "CHK-18").update(status="N/A", evidenceCoverage="NONE"))
    result = evaluator.evaluate(na_without_evidence)
    if claim(result, "CHK-18")["verdict"] != "UNRESOLVED":
        failures.append("N/A without applicability evidence was accepted")

    conclusive_partial = mutated(base, lambda d: row(d, "CHK-23").update(status="FAIL", evidenceCoverage="PARTIAL"))
    result = evaluator.evaluate(conclusive_partial)
    if control(result, "CHK-23")["outcome"] != "INEFFECTIVE":
        failures.append("conclusive FAIL was incorrectly erased by PARTIAL coverage")

    result = evaluator.evaluate(base)
    info_controls = [item for item in result["controlAssessments"] if item["outcome"] == "INFORMATIONAL"]
    if any(item["residualRisk"]["score"] != 0 for item in info_controls):
        failures.append("INFO inventory created residual risk")
    if any(item["attackConfirmation"] != "NOT_ASSERTED" for item in result["securityScenarios"]):
        failures.append("posture result overclaimed compromise/exploitation")

    with tempfile.TemporaryDirectory() as temp:
        bad = Path(temp) / "tampered.zip"
        with zipfile.ZipFile(base.source_name if Path(base.source_name).is_file() else FIXTURE) as source, zipfile.ZipFile(bad, "w") as target:
            for name in source.namelist():
                payload = source.read(name)
                if name.endswith("/results.json"):
                    doc = json.loads(payload); row(doc, "CHK-07")["status"] = "FAIL"
                    payload = json.dumps(doc).encode("utf-8")
                target.writestr(name, payload)
        try:
            load_evidence(bad)
            failures.append("tampered manifest package was accepted")
        except EvaluationError:
            pass

    if failures:
        print(f"[FAIL] false-positive guards: {len(failures)} error(s)")
        for item in failures: print(" - " + item)
        return 1
    print("[PASS] false-positive guards: missing PASS, unsupported N/A, INFO, partial failure, attack overclaim and tamper")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
