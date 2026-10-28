#!/usr/bin/env python3
from test_lib import *


def mutate_after(document):
    row(document, "CHK-23").update(status="PASS", evidenceCoverage="FULL", found=0, detail="Extension policy is enforced.")
    row(document, "CHK-07").update(status="FAIL", evidenceCoverage="FULL", found=1, detail="An essential provider is not registered.")


def main() -> int:
    base = fixture(); current = mutated(base, mutate_after); errors = []
    before = evaluate(base)
    after = evaluate(current, base)
    embedded = after["comparison"]
    standalone = build_comparison(before, after)
    if embedded is None: errors.append("embedded comparison missing")
    if embedded and embedded["summary"] != {"IMPROVED": 1, "REGRESSED": 1, "UNCHANGED": 62}: errors.append("embedded summary drift")
    if standalone["summary"] != {"IMPROVED": 1, "REGRESSED": 1, "UNCHANGED": 62}: errors.append("standalone summary drift")
    if len(standalone["controls"]) != 64 or len(standalone["scenarios"]) != 11: errors.append("comparison cardinality")
    changes = {row["checkId"]: row["change"] for row in standalone["controls"]}
    if changes.get("CHK-23") != "IMPROVED": errors.append("CHK-23 improvement")
    if changes.get("CHK-07") != "REGRESSED": errors.append("CHK-07 regression")
    if errors:
        print(f"[FAIL] canonical comparison: {len(errors)} error(s)")
        for error in errors: print(" - " + error)
        return 1
    print("[PASS] canonical comparison: embedded and standalone before/after with 64 controls and 11 scenarios")
    return 0


if __name__ == "__main__": raise SystemExit(main())
