#!/usr/bin/env python3
from __future__ import annotations

import json
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from test_lib import *


def mutate_after(document):
    row(document, "CHK-23").update(status="PASS", evidenceCoverage="FULL", found=0, detail="Extension policy is enforced.")
    row(document, "CHK-07").update(status="FAIL", evidenceCoverage="FULL", found=1, detail="An essential provider is not registered.")


def main() -> int:
    evaluator = engine(); baseline = fixture(); current = mutated(baseline, mutate_after); failures = []
    result = evaluator.evaluate(current, baseline)
    comparison = result["comparison"]
    if comparison is None:
        failures.append("comparison missing")
    else:
        by_check = {item["checkId"]: item for item in comparison["controls"]}
        if by_check["CHK-23"]["change"] != "IMPROVED" or by_check["CHK-23"]["delta"] >= 0:
            failures.append("CHK-23 improvement not detected")
        if by_check["CHK-07"]["change"] != "REGRESSED" or by_check["CHK-07"]["delta"] <= 0:
            failures.append("CHK-07 regression not detected")
        if comparison["summary"] != {"IMPROVED": 1, "REGRESSED": 1, "UNCHANGED": 62}:
            failures.append(f"before/after summary drift: {comparison['summary']}")
        if len(comparison["scenarios"]) != 11:
            failures.append("scenario before/after cardinality")
        if comparison["baselineRunId"] == comparison["currentRunId"]:
            failures.append("different evidence produced the same run ID")
    schema_dir = CP4 / "schemas"
    schemas = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in schema_dir.glob("*.json")}
    registry = Registry()
    for name, schema in schemas.items():
        registry = registry.with_resource(name, Resource.from_contents(schema))
    schema_errors = list(Draft202012Validator(schemas["evaluation-run.schema.json"], registry=registry).iter_errors(result))
    if schema_errors:
        failures.append("non-null before/after output failed JSON Schema: " + schema_errors[0].message)
    if failures:
        print(f"[FAIL] before/after: {len(failures)} error(s)")
        for item in failures: print(" - " + item)
        return 1
    print("[PASS] before/after: one improvement, one regression, 62 unchanged and 11 scenario deltas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
