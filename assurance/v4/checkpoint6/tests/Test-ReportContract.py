#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
import html
from pathlib import Path


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.scenarios: list[str] = []
        self.cards: list[str] = []
        self.meta: dict[str, str] = {}
        self._json = False
        self.json_text: list[str] = []
        self.runtime_scripts: list[str] = []
        self._runtime = False
        self._runtime_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.add(values["id"])
        if values.get("href", "").startswith("#"):
            self.hrefs.append(values["href"][1:])
        if values.get("data-scenario-id"):
            self.scenarios.append(values["data-scenario-id"])
        if values.get("data-action-card-id"):
            self.cards.append(values["data-action-card-id"])
        if tag == "meta" and values.get("name"):
            self.meta[values["name"]] = values.get("content", "")
        if tag == "script" and values.get("id") == "canonical-assessment":
            self._json = True
        elif tag == "script" and values.get("type") != "application/json":
            self._runtime = True
            self._runtime_text = []

    def handle_data(self, data: str) -> None:
        if self._json:
            self.json_text.append(data)
        if self._runtime:
            self._runtime_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json:
            self._json = False
        elif tag == "script" and self._runtime:
            self.runtime_scripts.append("".join(self._runtime_text))
            self._runtime = False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assessment", required=True, type=Path)
    parser.add_argument("--html", required=True, type=Path)
    args = parser.parse_args()
    expected = json.loads(args.assessment.read_text(encoding="utf-8-sig"))
    parsed = Parser()
    parsed.feed(args.html.read_text(encoding="utf-8"))
    embedded = json.loads("".join(parsed.json_text))
    errors: list[str] = []
    if embedded != expected:
        errors.append("embedded canonical contract is not byte-semantic equivalent to input")
    required = {"overview", "zt", "scenarios", "defense", "risks", "cards", "roadmap", "assets", "checks", "evidence", "comparison"}
    if expected["comparison"] is None:
        required = required - {"comparison"}  # PR17: Comparison section only when a baseline exists; disclosure stays (#comparison-null)
    if not required <= parsed.ids:
        errors.append(f"missing sections: {sorted(required - parsed.ids)}")
    chk_hrefs = {href for href in parsed.hrefs if href.startswith("chk-")}  # PR18: CHK pills link to Checks rows
    if chk_hrefs - parsed.ids:
        errors.append(f"CHK links without target: {sorted(chk_hrefs - parsed.ids)[:5]}")
    if set(parsed.hrefs) - chk_hrefs != required:
        errors.append("navigation targets do not match required sections")
    if parsed.meta.get("arc-report-contract") != "assessment-result.v4" or parsed.meta.get("arc-report-mode") != "render-only":
        errors.append("render-only contract metadata is absent")
    if parsed.scenarios != [f"AS{i:02d}" for i in range(1, 12)]:
        errors.append("scenario cardinality/order drift")
    if parsed.cards != [row["id"] for row in expected["actionCards"]]:
        errors.append("action-card cardinality/order drift")
    if len(expected["controlAssessments"]) != 64 or len(expected["traceability"]["evidence"]) != 64:
        errors.append("canonical 64-check evidence layer missing")
    if expected["comparison"] is None and "comparison-null" not in parsed.ids:
        errors.append("null comparison disclosure missing")
    if any("canonical-assessment" in script or "JSON.parse" in script for script in parsed.runtime_scripts):
        errors.append("browser JavaScript reads or interprets the canonical contract")
    visible = args.html.read_text(encoding="utf-8")
    for state in ("HYPOTHESIS", "POTENTIAL_RELEVANCE", "PROVIDER_IDENTIFIED", "VALIDATED"):
        if state not in visible:
            errors.append(f"scenario validation vocabulary missing: {state}")
    for stage in ("IDENTITY", "MANAGEMENT", "HOST", "DEFENSE"):
        if stage not in visible:
            errors.append(f"scenario path stage missing: {stage}")
    narrative_start = visible.find('id="executive-narrative"')
    if narrative_start < 0 or visible.count('id="executive-narrative"') != 1:
        errors.append("executive narrative missing or duplicated")
    else:
        block = visible[narrative_start:visible.find("</section>", narrative_start)]
        if html.escape(str(expected["metadata"]["runId"]), quote=True) not in block:
            errors.append("executive narrative does not cite the canonical runId")
        for group in ("controlOutcomes", "evidenceCoverage"):
            for key, value in expected["assurance"][group].items():
                if html.escape(f"{key}:{value}", quote=True) not in block:
                    errors.append(f"executive narrative missing {group} {key}:{value}")
        if expected["assurance"]["evidenceCoverage"].get("PARTIAL") and "narrative-partial" not in block:
            errors.append("executive narrative does not disclose PARTIAL coverage")
        for row in expected["roadmap"]["NOW"]:
            if html.escape(str(row["actionCardId"]), quote=True) not in block:
                errors.append(f"executive narrative missing NOW action {row['actionCardId']}")
        for row in expected["securityScenarios"]:
            if html.escape(str(row["attackConfirmation"]), quote=True) not in block:
                errors.append(f"executive narrative missing attackConfirmation {row['attackConfirmation']}")
        if expected["comparison"] is not None and html.escape(str(expected["comparison"]["baselineRunId"]), quote=True) not in block:
            errors.append("executive narrative does not cite the comparison baseline")
    plan_start = visible.find('id="action-plan"')
    if plan_start < 0 or visible.count('id="action-plan"') != 1:
        errors.append("action plan missing or duplicated")
    else:
        plan = visible[plan_start:visible.find("</section>", plan_start)]
        positions = [plan.find('data-plan-card="' + html.escape(str(row["actionCardId"]), quote=True) + '"') for row in expected["roadmap"]["NOW"]]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            errors.append("action plan does not follow the canonical Roadmap NOW order")
        plan_outcomes = {row["checkId"]: row["outcome"] for row in expected["controlAssessments"]}
        plan_statements = {row["checkId"]: row["statement"] for row in expected["traceability"]["observations"]}
        for row in expected["roadmap"]["NOW"]:
            for check_id in row["controlIds"]:
                statement = plan_statements.get(check_id)
                if plan_outcomes.get(check_id) in ("INEFFECTIVE", "AT_RISK") and statement is not None and html.escape(str(statement), quote=True) not in plan:
                    errors.append(f"action plan missing observed statement for {check_id}")
    if plan_start >= 0:
        trace_outcomes = {row["checkId"]: row["outcome"] for row in expected["controlAssessments"]}
        trace_evidence = {row["checkId"]: row for row in expected["traceability"]["evidence"]}
        trace_plan = visible[plan_start:visible.find("</section>", plan_start)]
        for row in expected["roadmap"]["NOW"]:
            for check_id in row["controlIds"]:
                if trace_outcomes.get(check_id) not in ("INEFFECTIVE", "AT_RISK"):
                    continue
                marker = 'data-trace="' + html.escape(str(check_id), quote=True) + '"'
                trace_start = trace_plan.find(marker)
                if trace_start < 0:
                    errors.append(f"evidence trace missing for {check_id}")
                    continue
                trace = trace_plan[trace_start:trace_plan.find("</details>", trace_start)]
                item = trace_evidence.get(check_id, {})
                for value in [item.get("detail"), *(item.get("sources") or [])]:
                    if value is not None and html.escape(str(value), quote=True) not in trace:
                        errors.append(f"evidence trace for {check_id} missing canonical value {value}")
    if errors:
        print(f"[FAIL] Checkpoint 6 report contract: {len(errors)} error(s)")
        for error in errors:
            print(" - " + error)
        return 1
    comparison_mode = "null comparison" if expected["comparison"] is None else "canonical before/after"
    print(f"[PASS] Checkpoint 6 report contract: render-only, 11 scenarios, 64 checks/evidence and {comparison_mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
