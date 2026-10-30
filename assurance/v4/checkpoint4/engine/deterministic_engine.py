#!/usr/bin/env python3
"""Deterministic Checkpoint 4 evaluation engine.

The engine consumes the collector's schema-v3 results (JSON or evidence ZIP) and
materializes a closed, traceable chain:
Evidence -> Observation -> Claim -> Control Assessment -> Zero Trust/Tier context
-> Security Scenario -> Prevent/Detect/Respond/Recover -> residual risk
-> Action Card -> NOW/30d/90d roadmap.

No clock, randomness, locale-sensitive ordering, network call, or LLM is used.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ENGINE_VERSION = "4.0.0-checkpoint4"
CHECKPOINT_VERSION = "4.0.0"
CONTROL_OUTCOME_RANK = {
    "NOT_APPLICABLE": 0,
    "INFORMATIONAL": 0,
    "EFFECTIVE": 1,
    "UNASSESSED": 3,
    "AT_RISK": 4,
    "INEFFECTIVE": 5,
}
SEVERITY_SCORE = {"High": 70, "Medium": 45, "Low": 20}
SCOPE_BONUS = {"T0": 15, "T1": 10, "Global": 8, "T2": 4}
PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
DEFENSE_FUNCTIONS = ("Prevent", "Detect", "Respond", "Recover")
CANONICAL_STATUSES = {
    "PASS", "WARN", "FAIL", "PARTIAL", "INFO", "N/A", "TODO", "MANUAL", "UNKNOWN", "ERROR"
}


class EvaluationError(ValueError):
    """Raised when an input violates a non-negotiable engine contract."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def stable_unique(values: Iterable[str]) -> list[str]:
    return sorted({str(v) for v in values if str(v)})


def clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def risk_level(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 35:
        return "MEDIUM"
    if score > 0:
        return "LOW"
    return "MINIMAL"


def priority_for(score: int) -> str:
    if score >= 80:
        return "P0"
    if score >= 60:
        return "P1"
    if score >= 35:
        return "P2"
    return "P3"


def horizon_for(priority: str) -> str:
    return "NOW" if priority in {"P0", "P1"} else "30d" if priority == "P2" else "90d"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


@dataclass(frozen=True)
class LoadedEvidence:
    document: dict[str, Any]
    source_name: str
    integrity: str
    members: tuple[str, ...]
    package_digest: str


def _verify_manifest(zf: zipfile.ZipFile, prefix: str, manifest: dict[str, Any]) -> None:
    names = set(zf.namelist())
    errors: list[str] = []
    for item in manifest.get("files", []):
        relative = str(item.get("path", ""))
        name = prefix + relative
        if not relative or name not in names:
            errors.append(f"manifest member missing: {relative}")
            continue
        payload = zf.read(name)
        expected_size = item.get("size")
        expected_hash = str(item.get("sha256", "")).lower()
        if expected_size is not None and len(payload) != int(expected_size):
            errors.append(f"manifest size mismatch: {relative}")
        if expected_hash and hashlib.sha256(payload).hexdigest().lower() != expected_hash:
            errors.append(f"manifest SHA-256 mismatch: {relative}")
    if errors:
        raise EvaluationError("; ".join(errors))


def load_evidence(path: str | Path) -> LoadedEvidence:
    source = Path(path)
    if not source.is_file():
        raise EvaluationError(f"evidence input not found: {source}")
    if source.suffix.lower() != ".zip":
        document = read_json(source)
        return LoadedEvidence(document, source.name, "NOT_PROVIDED", (source.name,), digest(document))

    package_bytes = source.read_bytes()
    with zipfile.ZipFile(source) as zf:
        result_names = sorted(n for n in zf.namelist() if n.endswith("/results.json") or n == "results.json")
        if len(result_names) != 1:
            raise EvaluationError(f"evidence ZIP must contain exactly one results.json; found {len(result_names)}")
        result_name = result_names[0]
        prefix = result_name[: -len("results.json")]
        manifest_name = prefix + "manifest.json"
        integrity = "NOT_PROVIDED"
        if manifest_name in zf.namelist():
            _verify_manifest(zf, prefix, json.loads(zf.read(manifest_name)))
            integrity = "VERIFIED"
        document = json.loads(zf.read(result_name))
        members = tuple(sorted(n[len(prefix):] for n in zf.namelist() if n.startswith(prefix) and not n.endswith("/")))
    return LoadedEvidence(document, source.name, integrity, members, hashlib.sha256(package_bytes).hexdigest())


def validate_input_contract(document: dict[str, Any]) -> None:
    if document.get("tool") != "arc-posture-review":
        raise EvaluationError("unsupported evidence tool")
    if document.get("schemaVersion") != 3:
        raise EvaluationError("Checkpoint 4 requires collector schemaVersion 3")
    rows = document.get("results")
    if not isinstance(rows, list):
        raise EvaluationError("results must be an array")
    ids = [str(row.get("id", "")) for row in rows]
    expected = [f"CHK-{index:02d}" for index in range(1, 65)]
    if sorted(ids) != expected or len(ids) != len(set(ids)):
        raise EvaluationError("results must contain CHK-01..CHK-64 exactly once")
    for row in rows:
        status = str(row.get("status", "UNKNOWN")).upper()
        if status not in CANONICAL_STATUSES:
            raise EvaluationError(f"{row.get('id')}: unsupported status {status}")


class DeterministicEvaluationEngine:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).resolve()

        integrated_cp3 = (
            self.project_root
            / "assurance"
            / "v4"
            / "checkpoint3"
            / "data"
        )

        package_cp3 = (
            self.project_root
            / "checkpoint3-v4"
            / "data"
        )

        if integrated_cp3.is_dir():
            cp3 = integrated_cp3
        elif package_cp3.is_dir():
            cp3 = package_cp3
        else:
            raise EvaluationError(
                "Checkpoint 3 data root could not be resolved"
            )
        self.checks = read_json(cp3 / "checks.enriched.json")
        self.assessments = read_json(cp3 / "control-assessments.json")
        self.scenarios = read_json(cp3 / "security-scenarios.json")
        self.coverage = read_json(cp3 / "defense-coverage.json")
        self.cards = read_json(cp3 / "action-cards.json")
        self.taxonomies = read_json(cp3 / "taxonomies.json")
        self.check_by_id = {row["id"]: row for row in self.checks}
        self.assessment_by_check = {row["checkId"]: row for row in self.assessments}
        self.coverage_by_check = {row["checkId"]: row for row in self.coverage}
        self.card_by_scenario = {row["scenarioId"]: row for row in self.cards}
        self.risk_by_id = {row["id"]: row for row in self.taxonomies["risks"]}
        self._validate_model_cardinality()

    def _validate_model_cardinality(self) -> None:
        expected = {f"CHK-{index:02d}" for index in range(1, 65)}
        if set(self.check_by_id) != expected or set(self.assessment_by_check) != expected:
            raise EvaluationError("Checkpoint 3 check/control model drift")
        if [row["id"] for row in self.scenarios] != [f"AS{i:02d}" for i in range(1, 12)]:
            raise EvaluationError("Checkpoint 3 scenario model drift")

    def evaluate(self, evidence: LoadedEvidence, baseline: LoadedEvidence | None = None) -> dict[str, Any]:
        current = self._evaluate_document(evidence)
        if baseline is not None:
            previous = self._evaluate_document(baseline)
            current["comparison"] = self._compare(previous, current)
        else:
            current["comparison"] = None
        current["outputDigest"] = digest({k: v for k, v in current.items() if k != "outputDigest"})
        return current

    def _evaluate_document(self, evidence: LoadedEvidence) -> dict[str, Any]:
        validate_input_contract(evidence.document)
        source_rows = {row["id"]: row for row in evidence.document["results"]}
        generated_at = str(evidence.document.get("startedAt") or min(
            (str(row.get("collectedAt")) for row in source_rows.values() if row.get("collectedAt")),
            default="1970-01-01T00:00:00Z",
        ))
        run_seed = {
            "engineVersion": ENGINE_VERSION,
            "modelDigest": self._model_digest(),
            "evidence": evidence.document,
        }
        run_id = "ER-" + digest(run_seed)[:20].upper()

        evidence_rows = []
        observations = []
        claims = []
        controls = []
        for check_id in sorted(self.check_by_id):
            model = self.check_by_id[check_id]
            raw = source_rows[check_id]
            ev = self._evidence_record(model, raw, evidence)
            observation = self._observation(model, raw, ev)
            claim = self._claim_evaluation(model, observation, ev)
            control = self._control_evaluation(model, claim, observation, ev)
            evidence_rows.append(ev)
            observations.append(observation)
            claims.append(claim)
            controls.append(control)

        scenarios = self._scenario_evaluations(controls)
        action_cards = self._action_cards(scenarios, controls)
        roadmap = self._roadmap(action_cards)
        counts = self._summary_counts(controls, scenarios, action_cards, roadmap)
        return {
            "contractVersion": "4.0.0",
            "checkpoint": 4,
            "engineVersion": ENGINE_VERSION,
            "runId": run_id,
            "generatedAt": generated_at,
            "deterministic": True,
            "source": {
                "name": evidence.source_name,
                "collectorVersion": str(evidence.document.get("version", "")),
                "schemaVersion": evidence.document.get("schemaVersion"),
                "integrity": evidence.integrity,
                "packageDigest": evidence.package_digest,
                "inputDigest": digest(evidence.document),
            },
            "model": {
                "checkpoint3Version": CHECKPOINT_VERSION,
                "digest": self._model_digest(),
                "preservedContracts": [
                    "collector-schema-v3",
                    "CHK-01..CHK-64",
                    "R01..R11",
                    "AS01..AS11",
                    "missing-evidence-never-PASS",
                    "Control-Result-independent-from-Evidence-Coverage",
                ],
            },
            "summary": counts,
            "evidence": evidence_rows,
            "observations": observations,
            "claims": claims,
            "controlAssessments": controls,
            "securityScenarios": scenarios,
            "actionCards": action_cards,
            "roadmap": roadmap,
        }

    def _model_digest(self) -> str:
        return digest({
            "checks": self.checks,
            "assessments": self.assessments,
            "scenarios": self.scenarios,
            "coverage": self.coverage,
            "cards": self.cards,
            "taxonomies": self.taxonomies,
        })

    @staticmethod
    def _source_refs(raw: dict[str, Any], model: dict[str, Any], members: tuple[str, ...]) -> list[str]:
        explicit = str(raw.get("evidenceSources", ""))
        refs = [part.strip() for part in re.split(r"[,;|]", explicit) if part.strip()]
        member_set = set(members)
        for dataset in model.get("sourceRefs", {}).get("datasets", []):
            candidate = f"data/{dataset}.json"
            if candidate in member_set:
                refs.append(candidate)
        if raw.get("file"):
            refs.append(str(raw["file"]))
        return stable_unique(refs)

    def _evidence_record(self, model: dict[str, Any], raw: dict[str, Any], loaded: LoadedEvidence) -> dict[str, Any]:
        check_id = model["id"]
        coverage = str(raw.get("evidenceCoverage", "NONE")).upper()
        if coverage not in {"FULL", "PARTIAL", "NONE", "ERROR"}:
            coverage = "ERROR"
        sources = self._source_refs(raw, model, loaded.members)
        required = stable_unique(model["claim"]["evidenceRequired"])
        available: list[str] = []
        if raw.get("evidenceScope") or loaded.document.get("scope"):
            available.append("scope")
        if raw.get("collectedAt") or loaded.document.get("startedAt"):
            available.append("timestamp")
        if sources:
            available.append("source")
        member_set = set(loaded.members)
        for field in required:
            if f"data/{field}.json" in member_set or any(ref.endswith(f"/{field}.json") and ref in member_set for ref in sources):
                available.append(field)
        available = stable_unique(available)
        missing = sorted(set(required) - set(available))
        return {
            "id": "EV-" + check_id,
            "checkId": check_id,
            "sourceStatus": str(raw.get("status", "UNKNOWN")).upper(),
            "coverage": coverage,
            "integrity": loaded.integrity,
            "scope": str(raw.get("evidenceScope") or digest(loaded.document.get("scope", {}))[:16]),
            "collectedAt": str(raw.get("collectedAt") or loaded.document.get("startedAt") or "1970-01-01T00:00:00Z"),
            "sources": sources,
            "requiredFields": required,
            "availableFields": available,
            "missingFields": missing,
            "found": int(raw.get("found") or 0),
            "detail": str(raw.get("detail", "")),
            "contentDigest": digest(raw),
        }

    @staticmethod
    def _observation(model: dict[str, Any], raw: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        check_id = model["id"]
        status = str(raw.get("status", "UNKNOWN")).upper()
        if status == "MANUAL":
            status = "TODO"
        flags: list[str] = []
        if evidence["missingFields"]:
            flags.append("MISSING_REQUIRED_EVIDENCE")
        if status == "PASS" and evidence["coverage"] != "FULL":
            flags.append("PASS_WITHOUT_FULL_EVIDENCE")
        if status == "N/A" and evidence["coverage"] != "FULL":
            flags.append("N_A_WITHOUT_FULL_EVIDENCE")
        if evidence["coverage"] == "ERROR":
            flags.append("COLLECTION_ERROR")

        if status in {"FAIL", "WARN"}:
            kind = "ADVERSE"
            applicability = "APPLICABLE"
        elif status == "PASS":
            kind = "FAVORABLE"
            applicability = "APPLICABLE"
        elif status == "INFO":
            kind = "INFORMATIONAL"
            applicability = "APPLICABLE"
        elif status == "N/A" and evidence["coverage"] == "FULL":
            kind = "NOT_APPLICABLE"
            applicability = "NOT_APPLICABLE"
        else:
            kind = "UNRESOLVED"
            applicability = "UNDETERMINED"
        return {
            "id": "OB-" + check_id,
            "checkId": check_id,
            "evidenceId": evidence["id"],
            "status": status,
            "kind": kind,
            "applicability": applicability,
            "severity": model["severity"],
            "found": evidence["found"],
            "statement": evidence["detail"] or "No detail supplied by the collector.",
            "falsePositiveGuards": sorted(flags),
        }

    @staticmethod
    def _claim_evaluation(model: dict[str, Any], observation: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        status = observation["status"]
        coverage = evidence["coverage"]
        missing = bool(evidence["missingFields"])
        reasons: list[str] = []
        if status == "INFO":
            verdict = "INFORMATIONAL"
            reasons.append("INFORMATIONAL_CONTROL")
        elif status == "N/A" and coverage == "FULL" and not missing:
            verdict = "NOT_APPLICABLE"
            reasons.append("APPLICABILITY_PROVEN")
        elif status == "PASS" and coverage == "FULL" and not missing:
            verdict = "SUPPORTED"
            reasons.append("PASS_WITH_COMPLETE_EVIDENCE")
        elif status == "FAIL" and coverage not in {"NONE", "ERROR"}:
            verdict = "REFUTED"
            reasons.append("CONCLUSIVE_ADVERSE_OBSERVATION")
        elif status == "WARN" and coverage not in {"NONE", "ERROR"}:
            verdict = "PARTIALLY_SUPPORTED"
            reasons.append("DEGRADED_CONTROL_OBSERVATION")
        else:
            verdict = "UNRESOLVED"
            reasons.append("INSUFFICIENT_EVIDENCE")
        if status == "PASS" and verdict != "SUPPORTED":
            reasons.append("PASS_SUPPRESSED_BY_EVIDENCE_GATE")
        if status == "N/A" and verdict != "NOT_APPLICABLE":
            reasons.append("N_A_SUPPRESSED_BY_APPLICABILITY_GATE")
        if missing:
            reasons.append("REQUIRED_FIELDS_MISSING")
        confidence = "HIGH" if coverage == "FULL" and not missing else "MEDIUM" if coverage == "PARTIAL" else "LOW"
        return {
            "id": "CL-" + model["id"],
            "checkId": model["id"],
            "observationId": observation["id"],
            "claimType": model["claim"]["claimType"],
            "assertion": model["resultCriteria"],
            "verdict": verdict,
            "confidence": confidence,
            "reasonCodes": sorted(set(reasons)),
            "absenceMeans": model["claim"]["absenceMeans"],
        }

    @staticmethod
    def _control_score(model: dict[str, Any], verdict: str) -> int:
        state_factor = {
            "REFUTED": 1.0,
            "PARTIALLY_SUPPORTED": 0.65,
            "UNRESOLVED": 0.50,
            "SUPPORTED": 0.0,
            "INFORMATIONAL": 0.0,
            "NOT_APPLICABLE": 0.0,
        }[verdict]
        scope_bonus = max((SCOPE_BONUS.get(scope, 0) for scope in model["securityScopes"]), default=0)
        return clamp((SEVERITY_SCORE[model["severity"]] + scope_bonus) * state_factor)

    def _control_evaluation(
        self, model: dict[str, Any], claim: dict[str, Any], observation: dict[str, Any], evidence: dict[str, Any]
    ) -> dict[str, Any]:
        outcome = {
            "SUPPORTED": "EFFECTIVE",
            "REFUTED": "INEFFECTIVE",
            "PARTIALLY_SUPPORTED": "AT_RISK",
            "UNRESOLVED": "UNASSESSED",
            "INFORMATIONAL": "INFORMATIONAL",
            "NOT_APPLICABLE": "NOT_APPLICABLE",
        }[claim["verdict"]]
        score = self._control_score(model, claim["verdict"])
        return {
            "id": "CE-" + model["id"],
            "checkId": model["id"],
            "evidenceId": evidence["id"],
            "observationId": observation["id"],
            "claimId": claim["id"],
            "outcome": outcome,
            "residualRisk": {"score": score, "level": risk_level(score)},
            "priority": priority_for(score),
            "securityModelStage": model["securityModelStage"],
            "zeroTrust": model["zeroTrust"],
            "securityScopes": model["securityScopes"],
            "riskIds": model["riskIds"],
            "scenarioIds": model["scenarioIds"],
            "securityBoundaryIds": model["securityBoundaryIds"],
            "defenseFunctions": model["defenseFunctions"],
            "mappingConfidence": model["mappingConfidence"],
            "trace": [evidence["id"], observation["id"], claim["id"]],
        }

    def _scenario_evaluations(self, controls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_check = {control["checkId"]: control for control in controls}
        rows: list[dict[str, Any]] = []
        for scenario in self.scenarios:
            related = [by_check[check_id] for check_id in scenario["controlCheckIds"]]
            ineffective = [row for row in related if row["outcome"] == "INEFFECTIVE"]
            at_risk = [row for row in related if row["outcome"] == "AT_RISK"]
            unassessed = [row for row in related if row["outcome"] == "UNASSESSED"]
            if ineffective:
                state = "OPEN"
                path = "EXPOSURE_INDICATED"
            elif at_risk:
                state = "ELEVATED"
                path = "WEAKNESS_INDICATED"
            elif unassessed:
                state = "UNRESOLVED"
                path = "NOT_EVALUABLE"
            else:
                state = "MITIGATED"
                path = "NOT_INDICATED"

            defense = {}
            for function in DEFENSE_FUNCTIONS:
                function_controls = [row for row in related if function in row["defenseFunctions"]]
                outcomes = {row["outcome"] for row in function_controls}
                if not function_controls:
                    status = "NOT_COVERED"
                elif "INEFFECTIVE" in outcomes:
                    status = "GAP"
                elif "AT_RISK" in outcomes:
                    status = "DEGRADED"
                elif "UNASSESSED" in outcomes:
                    status = "UNKNOWN"
                else:
                    status = "EFFECTIVE"
                defense[function] = {
                    "status": status,
                    "controlIds": sorted(row["checkId"] for row in function_controls),
                }

            static_card = self.card_by_scenario[scenario["id"]]
            base = 20 if static_card["priority"] == "P0" else 12
            ranked_scores = sorted((row["residualRisk"]["score"] for row in related), reverse=True)
            maximum = ranked_scores[0] if ranked_scores else 0
            top_average = sum(ranked_scores[:3]) / max(1, len(ranked_scores[:3]))
            gap_bonus = 4 * sum(1 for item in defense.values() if item["status"] == "GAP")
            unknown_bonus = min(10, 2 * len(unassessed))
            score = 0 if state == "MITIGATED" else clamp(base + 0.65 * maximum + 0.20 * top_average + gap_bonus + unknown_bonus)
            priority = priority_for(score)
            rows.append({
                "id": "SE-" + scenario["id"],
                "scenarioId": scenario["id"],
                "riskIds": scenario["riskIds"],
                "name": scenario["name"],
                "state": state,
                "attackPathAssessment": path,
                "attackConfirmation": "NOT_ASSERTED",
                "residualRisk": {"score": score, "level": risk_level(score)},
                "priority": priority,
                "securityBoundaryIds": scenario["securityBoundaryIds"],
                "controlIds": sorted(row["checkId"] for row in related),
                "triggeredControlIds": sorted(
                    (row["checkId"] for row in related if row["outcome"] in {"INEFFECTIVE", "AT_RISK", "UNASSESSED"}),
                    key=lambda cid: (-by_check[cid]["residualRisk"]["score"], cid),
                ),
                "defenseAssessment": defense,
                "guardrail": "A posture weakness is not evidence of exploitation or compromise.",
            })
        return rows

    def _action_cards(self, scenarios: list[dict[str, Any]], controls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_check = {control["checkId"]: control for control in controls}
        rows: list[dict[str, Any]] = []
        for scenario in scenarios:
            if scenario["state"] == "MITIGATED":
                continue
            template = self.card_by_scenario[scenario["scenarioId"]]
            triggered = scenario["triggeredControlIds"]
            priority = scenario["priority"]
            horizon = horizon_for(priority)
            top = triggered[:5]
            reasons = [
                f"{check_id}:{by_check[check_id]['outcome']}:{by_check[check_id]['residualRisk']['score']}"
                for check_id in top
            ]
            rows.append({
                "id": "ACI-" + template["riskId"],
                "templateId": template["id"],
                "riskId": template["riskId"],
                "scenarioId": template["scenarioId"],
                "title": template["title"],
                "priority": priority,
                "priorityScore": scenario["residualRisk"]["score"],
                "horizon": horizon,
                "owners": sorted(template["owners"]),
                "triggeredControlIds": triggered,
                "priorityReasons": reasons,
                "actions": template["actions"],
                "closureEvidence": template["closureEvidence"],
                "rollback": template["rollback"],
            })
        return sorted(rows, key=lambda row: (PRIORITY_RANK[row["priority"]], -row["priorityScore"], row["riskId"]))

    @staticmethod
    def _roadmap(cards: list[dict[str, Any]]) -> dict[str, Any]:
        buckets: dict[str, list[dict[str, Any]]] = {"NOW": [], "30d": [], "90d": []}
        due = {"NOW": 0, "30d": 30, "90d": 90}
        for card in cards:
            buckets[card["horizon"]].append({
                "actionCardId": card["id"],
                "riskId": card["riskId"],
                "scenarioId": card["scenarioId"],
                "priority": card["priority"],
                "priorityScore": card["priorityScore"],
                "dueInDays": due[card["horizon"]],
                "owners": card["owners"],
                "controlIds": card["triggeredControlIds"],
            })
        for horizon in buckets:
            buckets[horizon] = sorted(
                buckets[horizon],
                key=lambda row: (PRIORITY_RANK[row["priority"]], -row["priorityScore"], row["riskId"]),
            )
        return {
            "orderingRule": "priority asc, residual score desc, riskId asc",
            "NOW": buckets["NOW"],
            "30d": buckets["30d"],
            "90d": buckets["90d"],
        }

    @staticmethod
    def _summary_counts(
        controls: list[dict[str, Any]], scenarios: list[dict[str, Any]], cards: list[dict[str, Any]], roadmap: dict[str, Any]
    ) -> dict[str, Any]:
        def counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
            result: dict[str, int] = {}
            for row in rows:
                value = str(row[key])
                result[value] = result.get(value, 0) + 1
            return dict(sorted(result.items()))
        return {
            "controls": len(controls),
            "controlOutcomes": counts(controls, "outcome"),
            "scenarios": len(scenarios),
            "scenarioStates": counts(scenarios, "state"),
            "actionCards": len(cards),
            "roadmap": {horizon: len(roadmap[horizon]) for horizon in ("NOW", "30d", "90d")},
        }

    @staticmethod
    def _compare(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
        before_controls = {row["checkId"]: row for row in previous["controlAssessments"]}
        after_controls = {row["checkId"]: row for row in current["controlAssessments"]}
        control_rows = []
        for check_id in sorted(after_controls):
            before = before_controls[check_id]
            after = after_controls[check_id]
            before_score = before["residualRisk"]["score"]
            after_score = after["residualRisk"]["score"]
            change = "IMPROVED" if after_score < before_score else "REGRESSED" if after_score > before_score else "UNCHANGED"
            control_rows.append({
                "checkId": check_id,
                "beforeOutcome": before["outcome"],
                "afterOutcome": after["outcome"],
                "beforeScore": before_score,
                "afterScore": after_score,
                "delta": after_score - before_score,
                "change": change,
            })
        before_scenarios = {row["scenarioId"]: row for row in previous["securityScenarios"]}
        after_scenarios = {row["scenarioId"]: row for row in current["securityScenarios"]}
        scenario_rows = []
        for scenario_id in sorted(after_scenarios):
            before = before_scenarios[scenario_id]
            after = after_scenarios[scenario_id]
            before_score = before["residualRisk"]["score"]
            after_score = after["residualRisk"]["score"]
            change = "IMPROVED" if after_score < before_score else "REGRESSED" if after_score > before_score else "UNCHANGED"
            scenario_rows.append({
                "scenarioId": scenario_id,
                "beforeState": before["state"],
                "afterState": after["state"],
                "beforeScore": before_score,
                "afterScore": after_score,
                "delta": after_score - before_score,
                "change": change,
            })
        summary = {
            name: sum(1 for row in control_rows if row["change"] == name)
            for name in ("IMPROVED", "REGRESSED", "UNCHANGED")
        }
        return {
            "baselineRunId": previous["runId"],
            "currentRunId": current["runId"],
            "summary": summary,
            "controls": control_rows,
            "scenarios": scenario_rows,
        }


def write_evaluation(output: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
