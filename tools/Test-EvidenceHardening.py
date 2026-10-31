#!/usr/bin/env python3
"""Negative regressions for v4.1.0 evidence hardening (synthetic inputs only)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/evidence-hardening-negative.v4.1.0.json"
COLLECTOR = ROOT / "scripts/Invoke-ArcPostureReview.ps1"
TARGETS = ("CHK-42", "CHK-55", "CHK-57", "CHK-63")


def need(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def block(text: str, check_id: str) -> str:
    match = re.search(r"\$Eval\['" + re.escape(check_id) + r"'\] = \{(.*?)(?=\n\$Eval\['CHK-|\n# With a machine limit)", text, re.S)
    need(match is not None, f"collector block missing: {check_id}")
    return match.group(1)


def evaluate(check_id: str, source: dict) -> tuple[str, str]:
    if check_id == "CHK-42":
        valid = source["assessmentRows"] == 1 and source["successful"] and source["timestamped"] and source["countsValid"]
        negative = source["pending"] > 0 or source["extensionState"] != "Succeeded"
        unknown = not valid or source["authority"] != "AutomaticByPlatform"
        if negative:
            return "FAIL", "PARTIAL" if unknown else "FULL"
        return ("PARTIAL", "PARTIAL") if unknown else ("PASS", "FULL")
    if check_id == "CHK-55":
        explicit_failure = not source["recognized"] or source["compliance"] == "NonCompliant"
        unknown = source["recognized"] and (source["compliance"] != "Compliant" or not source["timestamped"])
        if explicit_failure:
            return "FAIL", "PARTIAL" if unknown else "FULL"
        return ("PARTIAL", "PARTIAL") if unknown else ("PASS", "FULL")
    if check_id == "CHK-57":
        gap = not source["mdeSucceeded"]
        if source["highOrMediumUnhealthy"]:
            return "FAIL", "PARTIAL" if gap else "FULL"
        if source["lowerUnhealthy"]:
            return "WARN", "PARTIAL" if gap else "FULL"
        return ("PARTIAL", "PARTIAL") if gap else ("PASS", "FULL")
    if check_id == "CHK-63":
        if source["free"]:
            return "FAIL", "PARTIAL" if source["unread"] else "FULL"
        if source["different"]:
            return "WARN", "PARTIAL" if source["unread"] else "FULL"
        return ("PARTIAL", "PARTIAL") if source["unread"] else ("PASS", "FULL")
    raise AssertionError(f"unsupported check: {check_id}")


def verify_static_contracts(text: str) -> None:
    markers = {
        "CHK-42": ("$duplicates", "validTimestamp", "assessmentStatus", "TryParse", "exactly one successful, timestamped assessment row", "Write-Result 'PARTIAL'"),
        "CHK-55": ("$baselinePattern", "lastChecked", "validTimestamp", "NonCompliant", "pending, missing, conflicting", "Write-Result 'PARTIAL'"),
        "CHK-57": ("[string]$k[$key] -ne 'Succeeded'", "Conclusive negative Defender evidence takes precedence", "Write-Result 'FAIL'", "Write-Result 'PARTIAL'"),
        "CHK-63": ("$notRead", "unread resource plan is unknown evidence", "Write-Result 'PARTIAL'", "Write-Result 'PASS'"),
    }
    for check_id, expected in markers.items():
        body = block(text, check_id)
        for marker in expected:
            need(marker in body, f"{check_id}: hardening marker missing: {marker}")
    chk57 = block(text, "CHK-57")
    need(chk57.index("if ($dHi.Count)") < chk57.index("if ($mdeGap.Count)"), "CHK-57: proxy gap masks conclusive Defender failure")
    chk63 = block(text, "CHK-63")
    need(chk63.index("if ($notRead.Count)") < chk63.index("Write-Result 'PASS'"), "CHK-63: unread evidence can reach PASS")


def verify_preserved_contracts() -> None:
    for locale in ("en-US", "pt-BR"):
        rows = json.loads((ROOT / f"criteria/checks.{locale}.json").read_text(encoding="utf-8"))
        need([row["id"] for row in rows] == [f"CHK-{i:02d}" for i in range(1, 65)], f"{locale}: canonical 64 checks drifted")
    scenarios = json.loads((ROOT / "assurance/v4/checkpoint3/data/security-scenarios.json").read_text(encoding="utf-8"))
    need([row["id"] for row in scenarios] == [f"AS{i:02d}" for i in range(1, 12)], "canonical 11 scenarios drifted")
    engine = (ROOT / "assurance/v4/checkpoint5/engine/canonical_v4.py").read_text(encoding="utf-8")
    need('CONTRACT_VERSION = "4.0.0"' in engine, "assessment contract version drift")
    schema = json.loads((ROOT / "assurance/v4/checkpoint5/schemas/assessment-result.v4.schema.json").read_text(encoding="utf-8"))
    need(schema["$defs"]["metadata"]["properties"]["contractVersion"]["const"] == "4.0.0", "assessment schema contract drift")


def main() -> int:
    try:
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        need(document["containsEnvironmentData"] is False and document["containsCustomerReport"] is False, "negative fixture privacy boundary")
        need({row["checkId"] for row in document["cases"]} == set(TARGETS), "negative fixture must cover all four checks")
        for case in document["cases"]:
            actual = evaluate(case["checkId"], case["input"])
            expected = (case["expected"]["status"], case["expected"]["coverage"])
            need(actual == expected, f"{case['id']}: expected {expected}, got {actual}")
        raw = FIXTURE.read_text(encoding="utf-8").lower()
        for forbidden in ("subscriptionid", "tenantid", "microsoft.com", "@"): 
            need(forbidden not in raw, f"negative fixture contains forbidden environment/customer token: {forbidden}")
        text = COLLECTOR.read_text(encoding="utf-8")
        verify_static_contracts(text)
        verify_preserved_contracts()
    except (AssertionError, KeyError, json.JSONDecodeError, OSError) as exc:
        print("[FAIL] v4.1.0 evidence hardening:", exc)
        return 1
    print("[PASS] v4.1.0 evidence hardening: 10 negative cases, 4 hardened checks, 64 controls, 11 scenarios, assessment contract 4.0.0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
