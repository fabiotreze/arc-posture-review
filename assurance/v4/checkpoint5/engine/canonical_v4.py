#!/usr/bin/env python3
"""Canonical Checkpoint 5 contract built on the deterministic Checkpoint 4 engine."""
from __future__ import annotations

import json
import importlib.util
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[4]
CP4 = REPO_ROOT / "assurance" / "v4" / "checkpoint4"
_CP4_ENGINE_PATH = CP4 / "engine" / "deterministic_engine.py"
_CP4_SPEC = importlib.util.spec_from_file_location("arc_posture_checkpoint4_engine", _CP4_ENGINE_PATH)
if _CP4_SPEC is None or _CP4_SPEC.loader is None:
    raise ImportError(f"cannot load Checkpoint 4 engine from {_CP4_ENGINE_PATH}")
_CP4_ENGINE = importlib.util.module_from_spec(_CP4_SPEC)
sys.modules[_CP4_SPEC.name] = _CP4_ENGINE
_CP4_SPEC.loader.exec_module(_CP4_ENGINE)
DeterministicEvaluationEngine = _CP4_ENGINE.DeterministicEvaluationEngine
EvaluationError = _CP4_ENGINE.EvaluationError
LoadedEvidence = _CP4_ENGINE.LoadedEvidence
digest = _CP4_ENGINE.digest
load_evidence = _CP4_ENGINE.load_evidence

CONTRACT_NAME = "assessment-result.v4"
CONTRACT_VERSION = "4.0.0"
PIPELINE_VERSION = "4.1.0-checkpoint5"
BASELINE_COMMIT = "2d512a3"
OUTCOMES = (
    "AT_RISK",
    "EFFECTIVE",
    "INEFFECTIVE",
    "INFORMATIONAL",
    "NOT_APPLICABLE",
    "UNASSESSED",
)
DEFENSE_FUNCTIONS = ("Prevent", "Detect", "Respond", "Recover")
DEFENSE_STATUSES = ("DEGRADED", "EFFECTIVE", "GAP", "NOT_COVERED", "UNKNOWN")


def _counts(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def _score_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [int(row["residualRisk"]["score"]) for row in rows]
    return {
        "count": len(rows),
        "maximum": max(scores, default=0),
        "minimum": min(scores, default=0),
        "total": sum(scores),
        "levels": _counts(row["residualRisk"]["level"] for row in rows),
    }


def _axis_summary(controls: list[dict[str, Any]], selector) -> list[dict[str, Any]]:
    names = sorted({name for row in controls for name in selector(row)})
    result: list[dict[str, Any]] = []
    for name in names:
        selected = [row for row in controls if name in selector(row)]
        result.append({
            "name": name,
            "controlIds": sorted(row["checkId"] for row in selected),
            "outcomeCounts": _counts(row["outcome"] for row in selected),
            "maximumResidualRiskScore": max((row["residualRisk"]["score"] for row in selected), default=0),
            "residualRiskScoreTotal": sum(row["residualRisk"]["score"] for row in selected),
        })
    return result


def _zero_trust(controls: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "principles": _axis_summary(controls, lambda row: row["zeroTrust"]["principles"]),
        "pillars": _axis_summary(controls, lambda row: row["zeroTrust"]["pillars"]),
        "controlMappings": [
            {
                "checkId": row["checkId"],
                "principles": sorted(row["zeroTrust"]["principles"]),
                "pillars": sorted(row["zeroTrust"]["pillars"]),
            }
            for row in sorted(controls, key=lambda item: item["checkId"])
        ],
    }


def _tiers(controls: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = ["T0", "T1", "T2", "Global"]
    rows = _axis_summary(controls, lambda row: row["securityScopes"])
    by_name = {row["name"]: row for row in rows}
    return {
        "order": ordered,
        "assessments": [by_name[name] for name in ordered if name in by_name],
        "controlMappings": [
            {"checkId": row["checkId"], "tiers": sorted(row["securityScopes"], key=lambda value: ordered.index(value))}
            for row in sorted(controls, key=lambda item: item["checkId"])
        ],
    }


def _defense_coverage(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    functions: dict[str, Any] = {}
    for function in DEFENSE_FUNCTIONS:
        states = [row["defenseAssessment"][function]["status"] for row in scenarios]
        functions[function] = {
            "statusCounts": _counts(states),
            "gapScenarioIds": sorted(
                row["scenarioId"]
                for row in scenarios
                if row["defenseAssessment"][function]["status"] in {"GAP", "DEGRADED", "UNKNOWN", "NOT_COVERED"}
            ),
        }
    return {
        "functions": functions,
        "scenarios": [
            {
                "scenarioId": row["scenarioId"],
                "assessment": {
                    function: {
                        "status": row["defenseAssessment"][function]["status"],
                        "controlIds": sorted(row["defenseAssessment"][function]["controlIds"]),
                    }
                    for function in DEFENSE_FUNCTIONS
                },
            }
            for row in sorted(scenarios, key=lambda item: item["scenarioId"])
        ],
    }


def _residual_risk(controls: list[dict[str, Any]], scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "controlSummary": _score_summary(controls),
        "scenarioSummary": _score_summary(scenarios),
        "controls": [
            {
                "checkId": row["checkId"],
                "outcome": row["outcome"],
                "score": row["residualRisk"]["score"],
                "level": row["residualRisk"]["level"],
                "priority": row["priority"],
            }
            for row in sorted(controls, key=lambda item: item["checkId"])
        ],
        "scenarios": [
            {
                "scenarioId": row["scenarioId"],
                "state": row["state"],
                "score": row["residualRisk"]["score"],
                "level": row["residualRisk"]["level"],
                "priority": row["priority"],
            }
            for row in sorted(scenarios, key=lambda item: item["scenarioId"])
        ],
    }


def _assurance(raw: dict[str, Any]) -> dict[str, Any]:
    evidence = raw["evidence"]
    claims = raw["claims"]
    controls = raw["controlAssessments"]
    observations = raw["observations"]
    return {
        "inputIntegrity": raw["source"]["integrity"],
        "evidenceRecordCount": len(evidence),
        "evidenceCoverage": _counts(row["coverage"] for row in evidence),
        "claimVerdicts": _counts(row["verdict"] for row in claims),
        "controlOutcomes": _counts(row["outcome"] for row in controls),
        "unresolvedControlIds": sorted(row["checkId"] for row in controls if row["outcome"] == "UNASSESSED"),
        "falsePositiveGuardCount": sum(len(row["falsePositiveGuards"]) for row in observations),
        "guarantees": [
            "64-controls-exactly-once",
            "attack-confirmation-not-asserted",
            "canonical-json-and-stable-ordering",
            "control-result-independent-from-evidence-coverage",
            "missing-evidence-never-pass",
            "no-clock-random-network-or-llm",
        ],
    }


def validate_canonical_assessment(document: dict[str, Any]) -> None:
    if document.get("metadata", {}).get("contractName") != CONTRACT_NAME:
        raise EvaluationError(f"expected metadata.contractName={CONTRACT_NAME}")
    controls = document.get("controlAssessments")
    if not isinstance(controls, list) or len(controls) != 64:
        raise EvaluationError("canonical assessment requires exactly 64 control assessments")
    expected = [f"CHK-{index:02d}" for index in range(1, 65)]
    if sorted(str(row.get("checkId")) for row in controls) != expected:
        raise EvaluationError("canonical assessment control IDs must be CHK-01..CHK-64 exactly once")
    scenarios = document.get("securityScenarios")
    if not isinstance(scenarios, list) or sorted(str(row.get("scenarioId")) for row in scenarios) != [f"AS{i:02d}" for i in range(1, 12)]:
        raise EvaluationError("canonical assessment scenarios must be AS01..AS11 exactly once")


_POTENTIAL = {"EXPOSURE_INDICATED", "WEAKNESS_INDICATED"}


def _attach_scenario_catalog(scenarios):
    """Copy hypothesis and attackPath from the CP3 catalog; derive validationState by rule."""
    import json as _json
    from pathlib import Path as _Path

    path = _Path(REPO_ROOT) / "assurance" / "v4" / "checkpoint3" / "data" / "security-scenarios.json"
    catalog = _json.loads(path.read_text(encoding="utf-8-sig"))
    rows = catalog if isinstance(catalog, list) else next(v for v in catalog.values() if isinstance(v, list))
    by_id = {row["id"]: row for row in rows}
    enriched = []
    for scenario in scenarios:
        entry = by_id.get(scenario["scenarioId"])
        if entry is None:
            raise EvaluationError("scenario %s is missing from the CP3 catalog" % scenario["scenarioId"])
        item = dict(scenario)
        item["hypothesis"] = entry["hypothesis"]
        item["attackPath"] = _json.loads(_json.dumps(entry["attackPath"]))
        item["validationState"] = (
            "POTENTIAL_RELEVANCE" if scenario["attackPathAssessment"] in _POTENTIAL else "HYPOTHESIS"
        )
        enriched.append(item)
    return enriched


def build_assessment(raw: dict[str, Any]) -> dict[str, Any]:
    controls = sorted(raw["controlAssessments"], key=lambda row: row["checkId"])
    scenarios = _attach_scenario_catalog(sorted(raw["securityScenarios"], key=lambda row: row["scenarioId"]))
    document: dict[str, Any] = {
        "metadata": {
            "contractName": CONTRACT_NAME,
            "contractVersion": CONTRACT_VERSION,
            "checkpoint": 5,
            "pipelineVersion": PIPELINE_VERSION,
            "engineVersion": raw["engineVersion"],
            "sourceCheckpointCommit": BASELINE_COMMIT,
            "runId": raw["runId"],
            "generatedAt": raw["generatedAt"],
            "deterministic": True,
            "source": raw["source"],
            "model": raw["model"],
            "pipeline": ["collector-schema-v3", "evaluation-engine", CONTRACT_NAME],
        },
        "assurance": _assurance(raw),
        "traceability": {
            "evidence": sorted(raw["evidence"], key=lambda row: row["checkId"]),
            "observations": sorted(raw["observations"], key=lambda row: row["checkId"]),
            "claims": sorted(raw["claims"], key=lambda row: row["checkId"]),
        },
        "controlAssessments": controls,
        "zeroTrust": _zero_trust(controls),
        "tiers": _tiers(controls),
        "securityScenarios": scenarios,
        "defenseCoverage": _defense_coverage(scenarios),
        "residualRisk": _residual_risk(controls, scenarios),
        "actionCards": raw["actionCards"],
        "roadmap": raw["roadmap"],
        "comparison": raw.get("comparison"),
    }
    document["outputDigest"] = digest(document)
    validate_canonical_assessment(document)
    return document


def evaluate(evidence: LoadedEvidence, baseline: LoadedEvidence | None = None, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    engine = DeterministicEvaluationEngine(repo_root)
    return build_assessment(engine.evaluate(evidence, baseline))


def evaluate_path(evidence_path: str | Path, baseline_path: str | Path | None = None) -> dict[str, Any]:
    evidence = load_evidence(evidence_path)
    baseline = load_evidence(baseline_path) if baseline_path else None
    return evaluate(evidence, baseline)


def comparison_payload(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    validate_canonical_assessment(before)
    validate_canonical_assessment(after)
    before_controls = {row["checkId"]: row for row in before["controlAssessments"]}
    after_controls = {row["checkId"]: row for row in after["controlAssessments"]}
    controls = []
    for check_id in sorted(after_controls):
        prior = before_controls[check_id]
        current = after_controls[check_id]
        before_score = prior["residualRisk"]["score"]
        after_score = current["residualRisk"]["score"]
        change = "IMPROVED" if after_score < before_score else "REGRESSED" if after_score > before_score else "UNCHANGED"
        controls.append({
            "checkId": check_id,
            "beforeOutcome": prior["outcome"],
            "afterOutcome": current["outcome"],
            "beforeScore": before_score,
            "afterScore": after_score,
            "delta": after_score - before_score,
            "change": change,
        })
    before_scenarios = {row["scenarioId"]: row for row in before["securityScenarios"]}
    after_scenarios = {row["scenarioId"]: row for row in after["securityScenarios"]}
    scenarios = []
    for scenario_id in sorted(after_scenarios):
        prior = before_scenarios[scenario_id]
        current = after_scenarios[scenario_id]
        before_score = prior["residualRisk"]["score"]
        after_score = current["residualRisk"]["score"]
        change = "IMPROVED" if after_score < before_score else "REGRESSED" if after_score > before_score else "UNCHANGED"
        scenarios.append({
            "scenarioId": scenario_id,
            "beforeState": prior["state"],
            "afterState": current["state"],
            "beforeScore": before_score,
            "afterScore": after_score,
            "delta": after_score - before_score,
            "change": change,
        })
    return {
        "baselineRunId": before["metadata"]["runId"],
        "currentRunId": after["metadata"]["runId"],
        "summary": {
            name: sum(1 for row in controls if row["change"] == name)
            for name in ("IMPROVED", "REGRESSED", "UNCHANGED")
        },
        "controls": controls,
        "scenarios": scenarios,
    }


def build_comparison(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    document: dict[str, Any] = {
        "contractName": "assessment-comparison.v4",
        "contractVersion": CONTRACT_VERSION,
        "generatedAt": after["metadata"]["generatedAt"],
        **comparison_payload(before, after),
    }
    document["outputDigest"] = digest(document)
    return document


def read_assessment(path: str | Path) -> dict[str, Any]:
    document = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    validate_canonical_assessment(document)
    return document


def write_json(document: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
