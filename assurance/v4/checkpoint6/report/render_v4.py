#!/usr/bin/env python3
"""Static renderer for assessment-result.v4.

The renderer validates and projects canonical values. Risk, priority, scenario
state, defense status and roadmap placement are Evaluation Engine outputs and
are never inferred or recalculated here or in browser JavaScript.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[4]
CP5_ENGINE = ROOT / "assurance" / "v4" / "checkpoint5" / "engine" / "canonical_v4.py"
_SPEC = importlib.util.spec_from_file_location("arc_posture_canonical_v4_for_report", CP5_ENGINE)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Cannot load canonical validator: {CP5_ENGINE}")
_CANONICAL = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _CANONICAL
_SPEC.loader.exec_module(_CANONICAL)

LOCALES = ("en-US", "pt-BR")
STAGES = ("IDENTITY", "MANAGEMENT", "HOST", "DEFENSE")
DEFENSE = ("Prevent", "Detect", "Respond", "Recover")

TEXT = {
    "en-US": {
        "title": "Arc Posture Review v4", "subtitle": "Canonical security posture report",
        "source": "Canonical source", "generated": "Generated", "integrity": "Input integrity",
        "overview": "Overview", "zt": "Zero Trust × Tier", "scenarios": "Security Scenarios",
        "defense": "Defense Coverage", "risks": "Risks", "cards": "Action Cards",
        "roadmap": "Roadmap", "assets": "Assets", "checks": "Checks", "evidence": "Evidence",
        "comparison": "Comparison", "noBaseline": "No baseline was supplied. comparison is null; no trend is asserted.",
        "outcomes": "Control outcomes", "coverage": "Evidence coverage", "verdicts": "Claim verdicts",
        "guarantees": "Assurance guarantees", "principles": "Principles", "pillars": "Pillars",
        "tiers": "Tier assessments", "mapping": "Canonical 64-check mapping",
        "id": "ID", "name": "Name", "state": "State", "validation": "Validation",
        "priority": "Priority", "score": "Score", "level": "Level", "controls": "Controls",
        "hypothesis": "Hypothesis", "guardrail": "Guardrail", "function": "Function",
        "gaps": "Gap scenarios", "status": "Status", "risk": "Risk", "owners": "Owners",
        "actions": "Actions", "closure": "Closure evidence", "rollback": "Rollback",
        "ordering": "Ordering rule", "due": "Due (days)", "sourcePackage": "Source package",
        "collector": "Collector", "schema": "Schema", "digest": "Digest", "scope": "Scope",
        "check": "Check", "outcome": "Outcome", "stage": "Stage", "boundaries": "Boundaries",
        "sourceFiles": "Source files", "detail": "Detail", "observation": "Observation",
        "claim": "Claim", "confidence": "Confidence", "found": "Found", "required": "Required fields",
        "missing": "Missing fields", "print": "Print / Save PDF", "expand": "Expand all",
        "collapse": "Collapse all", "model": "Model", "contract": "Contract",
        "baseline": "Baseline", "current": "Current", "change": "Change", "delta": "Delta", "verified": "Verified Improvement",
    },
    "pt-BR": {
        "title": "Arc Posture Review v4", "subtitle": "Relatório canônico de postura de segurança",
        "source": "Fonte canônica", "generated": "Gerado em", "integrity": "Integridade da entrada",
        "overview": "Visão geral", "zt": "Zero Trust × Tier", "scenarios": "Cenários de Segurança",
        "defense": "Cobertura de Defesa", "risks": "Riscos", "cards": "Action Cards",
        "roadmap": "Roadmap", "assets": "Assets", "checks": "Checks", "evidence": "Evidências",
        "comparison": "Comparação", "noBaseline": "Nenhum baseline foi fornecido. comparison é nulo; nenhuma tendência é afirmada.",
        "outcomes": "Resultados dos controles", "coverage": "Cobertura de evidências", "verdicts": "Vereditos das claims",
        "guarantees": "Garantias de assurance", "principles": "Princípios", "pillars": "Pilares",
        "tiers": "Avaliações por Tier", "mapping": "Mapeamento canônico dos 64 checks",
        "id": "ID", "name": "Nome", "state": "Estado", "validation": "Validação",
        "priority": "Prioridade", "score": "Score", "level": "Nível", "controls": "Controles",
        "hypothesis": "Hipótese", "guardrail": "Guardrail", "function": "Função",
        "gaps": "Cenários com gap", "status": "Status", "risk": "Risco", "owners": "Responsáveis",
        "actions": "Ações", "closure": "Evidências de encerramento", "rollback": "Rollback",
        "ordering": "Regra de ordenação", "due": "Prazo (dias)", "sourcePackage": "Pacote de origem",
        "collector": "Coletor", "schema": "Schema", "digest": "Digest", "scope": "Escopo",
        "check": "Check", "outcome": "Resultado", "stage": "Estágio", "boundaries": "Fronteiras",
        "sourceFiles": "Arquivos-fonte", "detail": "Detalhe", "observation": "Observação",
        "claim": "Claim", "confidence": "Confiança", "found": "Encontrado", "required": "Campos obrigatórios",
        "missing": "Campos ausentes", "print": "Imprimir / Salvar PDF", "expand": "Expandir tudo",
        "collapse": "Recolher tudo", "model": "Modelo", "contract": "Contrato",
        "baseline": "Baseline", "current": "Atual", "change": "Mudança", "delta": "Delta", "verified": "Melhoria Verificada",
    },
}

CSS = r"""
:root{--bg:#f4f7fb;--paper:#fff;--ink:#182233;--muted:#64748b;--line:#dbe4ef;--blue:#0f6cbd;--nav:#0b1f33;--good:#0b7a44;--warn:#a15c00;--bad:#b42318;--violet:#6938ef}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 "Segoe UI",Arial,sans-serif}a{color:inherit}.shell{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:100vh}.side{position:sticky;top:0;height:100vh;background:var(--nav);color:#fff;padding:24px 18px;overflow:auto}.brand{font-size:19px;font-weight:700}.brand small{display:block;color:#9ecbee;font-size:12px;font-weight:500;margin-top:4px}.side nav{display:grid;gap:3px;margin-top:22px}.side nav a{text-decoration:none;padding:8px 10px;border-radius:7px;color:#d7e6f5}.side nav a:hover,.side nav a.active{background:#173b5c;color:#fff}.main{min-width:0;padding:28px}.hero{background:linear-gradient(135deg,#092846,#0f6cbd);color:#fff;border-radius:16px;padding:28px;box-shadow:0 12px 30px #0b31551c}.hero h1{margin:0 0 5px;font-size:30px}.hero p{margin:0;color:#cfe8fb}.meta{display:flex;flex-wrap:wrap;gap:9px;margin-top:18px}.meta span,.badge{display:inline-flex;align-items:center;border-radius:999px;padding:4px 9px;background:#eaf2fb;color:#123b60;font-size:12px;font-weight:650}.hero .meta span{background:#ffffff1e;color:#fff;border:1px solid #ffffff2e}.toolbar{display:flex;gap:8px;margin:16px 0}.btn{border:1px solid var(--line);background:#fff;border-radius:8px;padding:8px 12px;font-weight:650;cursor:pointer}.section{scroll-margin-top:12px;margin:18px 0;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:20px;box-shadow:0 6px 18px #23344d0a}.section h2{margin:0 0 14px;font-size:22px}.section h3{margin:18px 0 9px;font-size:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:11px}.card{border:1px solid var(--line);border-radius:11px;padding:14px;min-width:0}.card h3,.card h4{margin:0 0 8px}.metric strong{display:block;font-size:25px;color:var(--blue)}.muted{color:var(--muted)}.mono{font:12px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:10px}table{border-collapse:collapse;width:100%;min-width:720px}th,td{border-bottom:1px solid var(--line);padding:9px 10px;text-align:left;vertical-align:top}th{background:#f7f9fc;color:#41546b;position:sticky;top:0}tr:last-child td{border-bottom:0}.pillset{display:flex;flex-wrap:wrap;gap:5px}.badge{background:#edf2f7;color:#34465b}.badge.P0,.badge.CRITICAL,.badge.INEFFECTIVE,.badge.GAP,.badge.REGRESSED{background:#fee4e2;color:var(--bad)}.badge.P1,.badge.HIGH,.badge.AT_RISK,.badge.DEGRADED,.badge.PARTIALLY_SUPPORTED{background:#fff1d6;color:var(--warn)}.badge.P2,.badge.MEDIUM,.badge.UNKNOWN,.badge.UNASSESSED,.badge.POTENTIAL_RELEVANCE{background:#f2eaff;color:var(--violet)}.badge.P3,.badge.MINIMAL,.badge.LOW,.badge.EFFECTIVE,.badge.SUPPORTED,.badge.VALIDATED,.badge.IMPROVED{background:#dcfae6;color:var(--good)}.badge.HYPOTHESIS,.badge.NOT_COVERED,.badge.NONE{background:#eef2f6;color:#586b80}.badge.PROVIDER_IDENTIFIED,.badge.FULL{background:#e0f2fe;color:#075985}.path{display:grid;grid-template-columns:repeat(7,minmax(70px,1fr));align-items:center;gap:6px;margin:12px 0}.node{border:1px solid #b9d4ec;background:#edf6fd;color:#164b76;padding:10px 7px;text-align:center;border-radius:9px;font-weight:700}.arrow{text-align:center;color:#7991a8;font-size:19px}.scenario{margin:12px 0;border:1px solid var(--line);border-radius:11px;overflow:hidden}.scenario summary{cursor:pointer;padding:13px 15px;background:#f8fafc;font-weight:700}.scenario .inside{padding:15px}.columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px}.notice{padding:14px;border-left:4px solid var(--blue);background:#eef7ff;border-radius:7px}.kv{display:grid;grid-template-columns:minmax(130px,190px) minmax(0,1fr);gap:5px 14px}.kv dt{color:var(--muted)}.kv dd{margin:0;overflow-wrap:anywhere}ul.compact{margin:6px 0;padding-left:19px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#0f172a;color:#dbeafe;padding:12px;border-radius:8px}.footer{color:var(--muted);text-align:center;padding:18px;overflow-wrap:anywhere}.only-print{display:none}
@media(max-width:900px){.shell{display:block}.side{position:static;height:auto}.side nav{display:flex;overflow:auto}.side nav a{white-space:nowrap}.main{padding:14px}.columns{grid-template-columns:1fr}.path{grid-template-columns:1fr}.arrow{transform:rotate(90deg)}.hero{padding:20px}.kv{grid-template-columns:1fr}.kv dd{margin-bottom:7px}}
@media print{body{background:#fff;font-size:10px}.shell{display:block}.side,.toolbar{display:none}.main{padding:0}.hero{box-shadow:none;border-radius:0;print-color-adjust:exact}.section{box-shadow:none;break-inside:avoid;margin:8mm 0}.only-print{display:block}details>.inside{display:block!important}details{break-inside:avoid}table{min-width:0}th{position:static}@page{size:landscape;margin:8mm}}
"""

JS = r"""'use strict';
(function(){
  const links=[...document.querySelectorAll('.side nav a')];
  const sections=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const activate=()=>{let current=sections[0];for(const section of sections){if(section.getBoundingClientRect().top<=90)current=section;}links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+current.id));};
  addEventListener('scroll',activate,{passive:true});activate();
  document.getElementById('print').addEventListener('click',()=>print());
  document.getElementById('expand').addEventListener('click',()=>document.querySelectorAll('details').forEach(x=>x.open=true));
  document.getElementById('collapse').addEventListener('click',()=>document.querySelectorAll('details').forEach(x=>x.open=false));
})();
"""


def esc(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        value = str(value).lower()
    return html.escape(str(value), quote=True)


def badge(value: Any) -> str:
    text = str(value)
    return f'<span class="badge {esc(text)}">{esc(text)}</span>'


def badges(values: Iterable[Any]) -> str:
    return '<span class="pillset">' + "".join(badge(value) for value in values) + "</span>"


def ul(values: Iterable[Any]) -> str:
    return '<ul class="compact">' + "".join(f"<li>{esc(value)}</li>" for value in values) + "</ul>"


def table(headers: list[str], rows: Iterable[Iterable[str]], classes: str = "") -> str:
    head = "".join(f"<th>{esc(value)}</th>" for value in headers)
    body = "".join("<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>" for row in rows)
    return f'<div class="tablewrap"><table class="{esc(classes)}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def count_cards(title: str, mapping: dict[str, Any]) -> str:
    inner = "".join(f'<div class="card metric"><span class="muted">{esc(key)}</span><strong>{esc(value)}</strong></div>' for key, value in mapping.items())
    return f"<h3>{esc(title)}</h3><div class=\"grid\">{inner}</div>"


def section(anchor: str, title: str, body: str) -> str:
    return f'<section class="section" id="{esc(anchor)}"><h2>{esc(title)}</h2>{body}</section>'


TEXT["en-US"].update({
    "validationTitle": "Not absolute truth.",
    "validationBody": (
        "This report reflects only the evidence collected, at one point in time and for one scope. "
        "Every finding must be validated and certified by qualified people against the real environment "
        "and official sources before any decision, remediation or customer commitment. "
        "It is informational: not a compliance certification, an audit opinion or a guarantee of security. "
        "Scenarios are hypotheses, and no attack is confirmed. "
        "Parts of this tool and its text were created with AI assistance and may contain errors. "
        "See DISCLAIMER.md in the repository."
    ),
})
TEXT["pt-BR"].update({
    "validationTitle": "Não é verdade absoluta.",
    "validationBody": (
        "Este relatório reflete apenas a evidência coletada, em um momento e escopo específicos. "
        "Todo achado precisa ser validado e certificado por profissionais qualificados, no ambiente real "
        "e em fontes oficiais, antes de qualquer decisão, correção ou compromisso com o cliente. "
        "O conteúdo é informativo: não é certificação de conformidade, parecer de auditoria "
        "nem garantia de segurança. Os cenários são hipóteses, e nenhum ataque é confirmado. "
        "Partes desta ferramenta e do seu texto foram criadas com apoio de IA e podem conter erros. "
        "Veja o DISCLAIMER.md no repositório."
    ),
})


def validate_document(document: dict[str, Any]) -> None:
    _CANONICAL.validate_canonical_assessment(document)
    semantic = dict(document)
    expected = semantic.pop("outputDigest", None)
    actual = _CANONICAL.digest(semantic)
    if expected != actual:
        raise ValueError("assessment-result.v4 outputDigest does not match its canonical content")
    states = {row.get("validationState") for row in document["securityScenarios"]}
    allowed = {"HYPOTHESIS", "POTENTIAL_RELEVANCE", "PROVIDER_IDENTIFIED", "VALIDATED"}
    if not states <= allowed or None in states:
        raise ValueError("securityScenarios contain an invalid validationState")
    for scenario in document["securityScenarios"]:
        path = scenario.get("attackPath", [])
        if [edge.get("from") for edge in path] != ["IDENTITY", "MANAGEMENT", "HOST"]:
            raise ValueError(f'{scenario.get("scenarioId")}: attackPath is not IDENTITY -> MANAGEMENT -> HOST -> DEFENSE')


def render(document: dict[str, Any], locale: str) -> str:
    validate_document(document)
    t = TEXT[locale]
    notice_html = (
        '<section class="notice" id="validation-notice" role="note">'
        f'<strong>{esc(t["validationTitle"])}</strong> {esc(t["validationBody"])}</section>'
    )
    meta = document["metadata"]
    assurance = document["assurance"]
    controls = document["controlAssessments"]
    scenarios = document["securityScenarios"]
    evidence = document["traceability"]["evidence"]
    observations = {row["checkId"]: row for row in document["traceability"]["observations"]}
    claims = {row["checkId"]: row for row in document["traceability"]["claims"]}
    zt = {row["checkId"]: row for row in document["zeroTrust"]["controlMappings"]}
    tier = {row["checkId"]: row for row in document["tiers"]["controlMappings"]}

    overview = (
        '<div class="grid">'
        f'<div class="card"><h3>{esc(t["contract"])}</h3><div class="mono">{esc(meta["contractName"])} · {esc(meta["contractVersion"])}</div><p>{esc(meta["pipelineVersion"])}</p></div>'
        f'<div class="card"><h3>Run</h3><div class="mono">{esc(meta["runId"])}</div><p>{esc(meta["generatedAt"])}</p></div>'
        f'<div class="card"><h3>{esc(t["sourcePackage"])}</h3><div>{esc(meta["source"]["name"])}</div><p>{badge(meta["source"]["integrity"])}</p></div>'
        f'<div class="card"><h3>{esc(t["model"])}</h3><div class="mono">{esc(meta["model"].get("digest"))}</div><p>{esc(meta["engineVersion"])}</p></div>'
        '</div>'
        + count_cards(t["outcomes"], assurance["controlOutcomes"])
        + count_cards(t["coverage"], assurance["evidenceCoverage"])
        + count_cards(t["verdicts"], assurance["claimVerdicts"])
        + f'<h3>{esc(t["guarantees"])}</h3>{ul(assurance["guarantees"])}'
    )

    axis_rows = []
    for row in document["zeroTrust"]["principles"]:
        axis_rows.append((esc(t["principles"]), esc(row["name"]), badges(row["controlIds"]), badges(f"{key}:{value}" for key, value in row["outcomeCounts"].items()), esc(row["maximumResidualRiskScore"])))
    for row in document["zeroTrust"]["pillars"]:
        axis_rows.append((esc(t["pillars"]), esc(row["name"]), badges(row["controlIds"]), badges(f"{key}:{value}" for key, value in row["outcomeCounts"].items()), esc(row["maximumResidualRiskScore"])))
    for row in document["tiers"]["assessments"]:
        axis_rows.append((esc(t["tiers"]), esc(row["name"]), badges(row["controlIds"]), badges(f"{key}:{value}" for key, value in row["outcomeCounts"].items()), esc(row["maximumResidualRiskScore"])))
    mapping_rows = ((esc(row["checkId"]), badges(zt[row["checkId"]]["principles"]), badges(zt[row["checkId"]]["pillars"]), badges(tier[row["checkId"]]["tiers"])) for row in controls)
    zero_trust = table(["Axis", t["name"], t["controls"], t["outcomes"], "Max risk"], axis_rows) + f'<h3>{esc(t["mapping"])}</h3>' + table([t["check"], t["principles"], t["pillars"], "Tier"], mapping_rows)

    scenario_blocks = []
    for row in scenarios:
        nodes = []
        for index, stage_name in enumerate(STAGES):
            if index:
                nodes.append('<div class="arrow" aria-hidden="true">→</div>')
            nodes.append(f'<div class="node">{esc(stage_name)}</div>')
        path_details = table(["From", "To", t["boundaries"], "Requires"], ((esc(edge["from"]), esc(edge["to"]), esc(edge["boundaryId"]), badges(edge["requires"])) for edge in row["attackPath"]))
        scenario_blocks.append(
            f'<details class="scenario" open data-scenario-id="{esc(row["scenarioId"])}"><summary>{esc(row["scenarioId"])} · {esc(row["name"])} · {badge(row["validationState"])} · {badge(row["priority"])}</summary><div class="inside">'
            f'<p><strong>{esc(t["hypothesis"])}:</strong> {esc(row["hypothesis"])}</p><div class="path">{"".join(nodes)}</div>{path_details}'
            f'<p>{badge(row["state"])} {badge(row["attackPathAssessment"])} {badge(row["attackConfirmation"])} {badge(row["residualRisk"]["level"])} <strong>{esc(t["score"])} {esc(row["residualRisk"]["score"])}</strong></p>'
            f'<p><strong>{esc(t["controls"])}:</strong> {badges(row["controlIds"])}<br><strong>Triggered:</strong> {badges(row["triggeredControlIds"])}</p>'
            f'<p class="notice"><strong>{esc(t["guardrail"])}:</strong> {esc(row["guardrail"])}</p></div></details>'
        )
    scenario_html = "".join(scenario_blocks)

    function_rows = ((esc(name), badges(f"{key}:{value}" for key, value in document["defenseCoverage"]["functions"][name]["statusCounts"].items()), badges(document["defenseCoverage"]["functions"][name]["gapScenarioIds"])) for name in DEFENSE)
    defense_rows = []
    for row in document["defenseCoverage"]["scenarios"]:
        defense_rows.append((esc(row["scenarioId"]), *(badge(row["assessment"][name]["status"]) + '<br>' + badges(row["assessment"][name]["controlIds"]) for name in DEFENSE)))
    defense_html = table([t["function"], t["status"], t["gaps"]], function_rows) + "<h3>Scenario × function</h3>" + table([t["id"], *DEFENSE], defense_rows)

    control_risks = table([t["check"], t["outcome"], t["score"], t["level"], t["priority"]], ((esc(row["checkId"]), badge(row["outcome"]), esc(row["score"]), badge(row["level"]), badge(row["priority"])) for row in document["residualRisk"]["controls"]))
    scenario_risks = table([t["id"], t["state"], t["score"], t["level"], t["priority"]], ((esc(row["scenarioId"]), badge(row["state"]), esc(row["score"]), badge(row["level"]), badge(row["priority"])) for row in document["residualRisk"]["scenarios"]))
    risk_html = f'<h3>{esc(t["checks"])}</h3>{control_risks}<h3>{esc(t["scenarios"])}</h3>{scenario_risks}'

    card_blocks = []
    for row in document["actionCards"]:
        card_blocks.append(f'<div class="card" data-action-card-id="{esc(row["id"])}"><h3>{esc(row["id"])} · {esc(row["title"])}</h3><p>{badge(row["priority"])} {badge(row["horizon"])} <strong>{esc(t["score"])} {esc(row["priorityScore"])}</strong></p><p><strong>{esc(t["owners"])}:</strong> {badges(row["owners"])}</p><h4>{esc(t["actions"])}</h4>{ul(row["actions"])}<h4>{esc(t["closure"])}</h4>{ul(row["closureEvidence"])}<p><strong>{esc(t["rollback"])}:</strong> {esc(row["rollback"])}</p><p>{badges(row["triggeredControlIds"])}</p></div>')
    cards_html = '<div class="grid">' + "".join(card_blocks) + '</div>'

    roadmap_columns = []
    for horizon in ("NOW", "30d", "90d"):
        rows = document["roadmap"][horizon]
        roadmap_columns.append(f'<div class="card"><h3>{esc(horizon)}</h3>' + ("".join(f'<div class="card"><strong>{esc(row["actionCardId"])}</strong> {badge(row["priority"])}<br>{esc(row["scenarioId"])} · {esc(row["riskId"])} · {esc(t["score"])} {esc(row["priorityScore"])}<br><span class="muted">{esc(t["due"])}: {esc(row["dueInDays"])} · {esc(t["owners"])}: {esc(", ".join(row["owners"]))}</span><br>{badges(row["controlIds"])}</div>' for row in rows) or '<p class="muted">—</p>') + '</div>')
    roadmap_html = f'<p><strong>{esc(t["ordering"])}:</strong> {esc(document["roadmap"]["orderingRule"])}</p><div class="columns">{"".join(roadmap_columns)}</div>'

    source = meta["source"]
    assets_html = f'<dl class="kv"><dt>{esc(t["sourcePackage"])}</dt><dd>{esc(source["name"])}</dd><dt>{esc(t["collector"])}</dt><dd>{esc(source["collectorVersion"])}</dd><dt>{esc(t["schema"])}</dt><dd>{esc(source["schemaVersion"])}</dd><dt>{esc(t["integrity"])}</dt><dd>{badge(source["integrity"])}</dd><dt>Package digest</dt><dd class="mono">{esc(source["packageDigest"])}</dd><dt>Input digest</dt><dd class="mono">{esc(source["inputDigest"])}</dd><dt>Pipeline</dt><dd>{badges(meta["pipeline"])}</dd></dl>'

    check_rows = ((esc(row["checkId"]), badge(row["outcome"]), esc(row["securityModelStage"]), badges(row["securityScopes"]), badges(row["riskIds"]), badges(row["scenarioIds"]), badge(row["priority"]), esc(row["residualRisk"]["score"])) for row in controls)
    checks_html = table([t["check"], t["outcome"], t["stage"], "Tier", t["risk"], t["scenarios"], t["priority"], t["score"]], check_rows)

    evidence_rows = []
    for row in evidence:
        check_id = row["checkId"]
        observation = observations[check_id]
        claim = claims[check_id]
        evidence_rows.append((esc(check_id), badge(row["coverage"]), esc(row["scope"]), badges(row["sources"]), esc(row["detail"]), badge(observation["status"]) + " " + esc(observation["statement"]), badge(claim["verdict"]) + " " + esc(claim["assertion"]), badge(claim["confidence"])))
    evidence_html = table([t["check"], t["coverage"], t["scope"], t["sourceFiles"], t["detail"], t["observation"], t["claim"], t["confidence"]], evidence_rows)

    comparison = document["comparison"]
    if comparison is None:
        comparison_html = f'<p class="notice" id="comparison-null">{esc(t["noBaseline"])}</p>'
    else:
        summary = count_cards(t["comparison"], comparison["summary"])
        def change_cell(row: dict[str, Any]) -> str:
            rendered = badge(row["change"])
            if row["change"] == "IMPROVED":
                rendered += f' <span class="badge VERIFIED_IMPROVEMENT">{esc(t["verified"])}</span>'
            return rendered
        rows = ((esc(row["checkId"]), badge(row["beforeOutcome"]), badge(row["afterOutcome"]), esc(row["beforeScore"]), esc(row["afterScore"]), esc(row["delta"]), change_cell(row)) for row in comparison["controls"])
        scenario_rows = ((esc(row["scenarioId"]), badge(row["beforeState"]), badge(row["afterState"]), esc(row["beforeScore"]), esc(row["afterScore"]), esc(row["delta"]), change_cell(row)) for row in comparison["scenarios"])
        comparison_html = (
            f'<p><strong>{esc(t["baseline"])}:</strong> {esc(comparison["baselineRunId"])} · '
            f'<strong>{esc(t["current"])}:</strong> {esc(comparison["currentRunId"])}</p>'
            + summary
            + f'<h3>{esc(t["checks"])}</h3>'
            + table([t["check"], t["baseline"], t["current"], "Before score", "After score", t["delta"], t["change"]], rows)
            + f'<h3>{esc(t["scenarios"])}</h3>'
            + table([t["id"], t["baseline"], t["current"], "Before score", "After score", t["delta"], t["change"]], scenario_rows)
        )

    anchors = [("overview", t["overview"]), ("zt", t["zt"]), ("scenarios", t["scenarios"]), ("defense", t["defense"]), ("risks", t["risks"]), ("cards", t["cards"]), ("roadmap", t["roadmap"]), ("assets", t["assets"]), ("checks", t["checks"]), ("evidence", t["evidence"]), ("comparison", t["comparison"])]
    nav = "".join(f'<a href="#{anchor}">{esc(label)}</a>' for anchor, label in anchors)
    sections = "".join([
        section("overview", t["overview"], overview), section("zt", t["zt"], zero_trust),
        section("scenarios", t["scenarios"], scenario_html), section("defense", t["defense"], defense_html),
        section("risks", t["risks"], risk_html), section("cards", t["cards"], cards_html),
        section("roadmap", t["roadmap"], roadmap_html), section("assets", t["assets"], assets_html),
        section("checks", t["checks"], checks_html), section("evidence", t["evidence"], evidence_html),
        section("comparison", t["comparison"], comparison_html),
    ])
    script_digest = base64.b64encode(hashlib.sha256(JS.encode("utf-8")).digest()).decode("ascii")
    canonical_json = json.dumps(document, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="{esc(locale)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="arc-report-contract" content="assessment-result.v4"><meta name="arc-report-mode" content="render-only"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-{script_digest}'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'"><title>{esc(t["title"])}</title><style>{CSS}</style></head>
<body><div class="shell"><aside class="side"><div class="brand">{esc(t["title"])}<small>{esc(t["subtitle"])}</small></div><nav>{nav}</nav></aside><main class="main">{notice_html}<header class="hero"><h1>{esc(t["title"])}</h1><p>{esc(t["subtitle"])}</p><div class="meta"><span>{esc(t["source"])}: assessment-result.v4.json</span><span>{esc(meta["runId"])}</span><span>{esc(t["generated"])}: {esc(meta["generatedAt"])}</span><span>{esc(t["integrity"])}: {esc(source["integrity"])}</span></div></header><div class="toolbar"><button class="btn" id="print">{esc(t["print"])}</button><button class="btn" id="expand">{esc(t["expand"])}</button><button class="btn" id="collapse">{esc(t["collapse"])}</button></div>{sections}<footer class="footer">assessment-result.v4 · {esc(document["outputDigest"])}<br>Render-only report: risk, priority, scenario and roadmap values are supplied by the Evaluation Engine.</footer></main></div><script type="application/json" id="canonical-assessment">{canonical_json}</script><script>{JS}</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Render assessment-result.v4 as a static HTML report")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--locale", choices=LOCALES, default="en-US")
    args = parser.parse_args()
    document = json.loads(args.input.read_text(encoding="utf-8-sig"))
    output = render(document, args.locale)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8", newline="\n")
    print(f"[PASS] rendered {args.locale} assessment-result.v4 -> {args.output}")
    return 0


STATUS_COLORS_CSS = r"""
.badge{border:1px solid transparent;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.badge.P0,.badge.CRITICAL,.badge.INEFFECTIVE,.badge.GAP,.badge.REGRESSED,.badge.FAIL,.badge.REFUTED,.badge[class*=" INEFFECTIVE:"],.badge[class*=" GAP:"]{background:#b42318;color:#fff}
.badge.P1,.badge.HIGH,.badge.AT_RISK,.badge.DEGRADED,.badge.PARTIALLY_SUPPORTED,.badge.WARN,.badge.ELEVATED,.badge.WEAKNESS_INDICATED,.badge[class*=" AT_RISK:"],.badge[class*=" DEGRADED:"]{background:#b54708;color:#fff}
.badge.P2,.badge.MEDIUM,.badge.UNKNOWN,.badge.UNASSESSED,.badge.POTENTIAL_RELEVANCE,.badge.UNRESOLVED,.badge.PARTIAL,.badge.OPEN,.badge.TODO,.badge.EXPOSURE_INDICATED,.badge.NOT_EVALUABLE,.badge[class*=" UNASSESSED:"],.badge[class*=" UNKNOWN:"]{background:#5925dc;color:#fff}
.badge.P3,.badge.MINIMAL,.badge.LOW,.badge.EFFECTIVE,.badge.SUPPORTED,.badge.VALIDATED,.badge.IMPROVED,.badge.PASS,.badge.VERIFIED,.badge.MITIGATED,.badge.NOT_INDICATED,.badge[class*=" EFFECTIVE:"]{background:#067647;color:#fff}
.badge.INFO,.badge.INFORMATIONAL,.badge.NOT_ASSERTED,.badge.N\/A,.badge.NOW,.badge.PROVIDER_IDENTIFIED,.badge.FULL,.badge[class*=" INFORMATIONAL:"]{background:#175cd3;color:#fff}
.badge.HYPOTHESIS,.badge.NOT_COVERED,.badge.NONE,.badge.UNCHANGED,.badge[class*=" NOT_COVERED:"]{background:#475467;color:#fff}
"""

_render_without_status_colors = render


def render(document, locale):
    html = _render_without_status_colors(document, locale)
    if "</style>" not in html:
        raise ValueError("report has no style block")
    return html.replace("</style>", STATUS_COLORS_CSS + "</style>", 1)



# --- Executive narrative (render-only projection of canonical fields) ---------
TEXT["en-US"].update({
    "narrativeTitle": "Executive narrative",
    "narrativeRun": "Run {run} assessed {n} controls. Control outcomes:",
    "narrativeCoverage": "Evidence coverage:",
    "narrativePartial": "{k} control(s) have PARTIAL evidence coverage; their outcomes must not be read as fully evidenced.",
    "narrativeNow": "Roadmap NOW ({n}):",
    "narrativeNowEmpty": "Roadmap NOW: no action in this horizon.",
    "narrativeScenarios": "{n} security scenarios are posture hypotheses. Attack confirmation:",
    "narrativeNoAttack": "This report does not confirm any attack.",
    "narrativeNoBaseline": "No baseline was supplied, so no trend is asserted.",
    "narrativeComparison": "Compared with baseline {run}:",
    "narrativeSource": "Every value in this narrative is read from assessment-result.v4; nothing is recalculated.",
})
TEXT["pt-BR"].update({
    "narrativeTitle": "Narrativa executiva",
    "narrativeRun": "A execução {run} avaliou {n} controles. Resultados dos controles:",
    "narrativeCoverage": "Cobertura de evidências:",
    "narrativePartial": "{k} controle(s) têm cobertura de evidência PARTIAL; seus resultados não devem ser lidos como totalmente evidenciados.",
    "narrativeNow": "Roadmap NOW ({n}):",
    "narrativeNowEmpty": "Roadmap NOW: nenhuma ação neste horizonte.",
    "narrativeScenarios": "{n} cenários de segurança são hipóteses de postura. Confirmação de ataque:",
    "narrativeNoAttack": "Este relatório não confirma nenhum ataque.",
    "narrativeNoBaseline": "Nenhum baseline foi fornecido; nenhuma tendência é afirmada.",
    "narrativeComparison": "Comparado ao baseline {run}:",
    "narrativeSource": "Todos os valores desta narrativa vêm do assessment-result.v4; nada é recalculado.",
})

NARRATIVE_CSS = r"""
.narrative{margin:16px 0}.narrative h2{margin:0 0 8px;font-size:18px}.narrative p{margin:6px 0}.narrative .narrative-partial{font-weight:650}
.badge[class*=" FULL:"]{background:#175cd3;color:#fff}.badge[class*=" PARTIAL:"]{background:#5925dc;color:#fff}.badge[class*=" NONE:"]{background:#475467;color:#fff}
.badge[class*=" IMPROVED:"]{background:#067647;color:#fff}.badge[class*=" REGRESSED:"]{background:#b42318;color:#fff}.badge[class*=" UNCHANGED:"]{background:#475467;color:#fff}
@media print{.narrative{break-inside:avoid}}
"""


def narrative_html(document: dict[str, Any], locale: str) -> str:
    t = TEXT[locale]
    meta = document["metadata"]
    assurance = document["assurance"]
    now = document["roadmap"]["NOW"]
    scenarios = document["securityScenarios"]
    comparison = document["comparison"]
    confirmations = list(dict.fromkeys(row["attackConfirmation"] for row in scenarios))
    partial = assurance["evidenceCoverage"].get("PARTIAL")
    run_text = t["narrativeRun"].format(run=meta["runId"], n=len(document["controlAssessments"]))
    parts = [
        f'<p>{esc(run_text)} {badges(f"{key}:{value}" for key, value in assurance["controlOutcomes"].items())}</p>',
        f'<p>{esc(t["narrativeCoverage"])} {badges(f"{key}:{value}" for key, value in assurance["evidenceCoverage"].items())}'
        + (f' <span class="narrative-partial">{esc(t["narrativePartial"].format(k=partial))}</span>' if partial else "")
        + "</p>",
        (f'<p>{esc(t["narrativeNow"].format(n=len(now)))} {badges(row["actionCardId"] for row in now)}</p>'
         if now else f'<p>{esc(t["narrativeNowEmpty"])}</p>'),
        f'<p>{esc(t["narrativeScenarios"].format(n=len(scenarios)))} {badges(confirmations)} {esc(t["narrativeNoAttack"])}</p>',
        (f'<p>{esc(t["narrativeNoBaseline"])}</p>' if comparison is None else
         f'<p>{esc(t["narrativeComparison"].format(run=comparison["baselineRunId"]))} '
         f'{badges(f"{key}:{value}" for key, value in comparison["summary"].items())}</p>'),
        f'<p class="muted">{esc(t["narrativeSource"])}</p>',
    ]
    return (
        f'<section class="notice narrative" id="executive-narrative" aria-label="{esc(t["narrativeTitle"])}">'
        f'<h2>{esc(t["narrativeTitle"])}</h2>{"".join(parts)}</section>'
    )


_render_without_narrative = render


def render(document, locale):
    html_text = _render_without_narrative(document, locale)
    anchor = '<div class="toolbar">'
    if html_text.count(anchor) != 1 or "</style>" not in html_text:
        raise ValueError("report layout anchor for the executive narrative not found")
    html_text = html_text.replace("</style>", NARRATIVE_CSS + "</style>", 1)
    return html_text.replace(anchor, narrative_html(document, locale) + anchor, 1)



# --- Execution-first top: labels, narrative v2 and action plan (render-only) ---
STATUS_LABELS = {
    "en-US": {
        "INEFFECTIVE": "Failing", "AT_RISK": "At risk", "EFFECTIVE": "Effective",
        "INFORMATIONAL": "Informational", "UNASSESSED": "Not assessed",
        "FULL": "Full evidence", "PARTIAL": "Partial evidence", "NONE": "No evidence",
        "IMPROVED": "Improved", "REGRESSED": "Regressed", "UNCHANGED": "Unchanged",
    },
    "pt-BR": {
        "INEFFECTIVE": "Falha", "AT_RISK": "Em risco", "EFFECTIVE": "Efetivo",
        "INFORMATIONAL": "Informativo", "UNASSESSED": "Não avaliado",
        "FULL": "Evidência completa", "PARTIAL": "Evidência parcial", "NONE": "Sem evidência",
        "IMPROVED": "Melhorou", "REGRESSED": "Piorou", "UNCHANGED": "Sem mudança",
    },
}
TEXT["en-US"].update({
    "narrativeRun": "Run {run} assessed {n} controls.",
    "narrativeGap": "{u} of {n} controls could not be assessed because evidence is missing. Complete the collection before drawing conclusions.",
    "narrativeNow": "Roadmap NOW - {n} action(s), detailed in the action plan below:",
    "planTitle": "Action plan - NOW",
    "planIntro": "Canonical roadmap order. Each action lists only its failing or at-risk checks with what was observed; full detail is in Action Cards.",
    "planOwners": "Owners", "planDue": "Due", "planDays": "days",
    "planOthers": "Other checks in this action:",
    "planNoFailing": "No failing or at-risk check in this action; see Action Cards.",
    "planHowTo": "How to execute each action", "planClosure": "Closure evidence",
    "planEmpty": "No action in the NOW horizon.",
})
TEXT["pt-BR"].update({
    "narrativeRun": "A execução {run} avaliou {n} controles.",
    "narrativeGap": "{u} de {n} controles não puderam ser avaliados por falta de evidência. Complete a coleta antes de tirar conclusões.",
    "narrativeNow": "Roadmap NOW - {n} ação(ões), detalhadas no plano de ação abaixo:",
    "planTitle": "Plano de ação - agora (NOW)",
    "planIntro": "Ordem do roadmap canônico. Cada ação mostra só os checks com falha ou em risco e o que foi observado; o detalhe completo está em Action Cards.",
    "planOwners": "Responsáveis", "planDue": "Prazo", "planDays": "dias",
    "planOthers": "Outros checks desta ação:",
    "planNoFailing": "Nenhum check com falha ou em risco nesta ação; veja Action Cards.",
    "planHowTo": "Como executar cada ação", "planClosure": "Evidência de encerramento",
    "planEmpty": "Nenhuma ação no horizonte NOW.",
})

PLAN_CSS = r"""
.kpis{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 10px}
.kpi{display:inline-flex;align-items:baseline;gap:6px;border-radius:8px;padding:5px 10px;font-size:13px;background:#f1f5f9;color:#1f2937;border-left:5px solid #94a3b8;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.kpi b{font-size:18px}
.k-INEFFECTIVE,.k-REGRESSED{border-left-color:#b42318}.k-AT_RISK,.k-PARTIAL{border-left-color:#b54708}
.k-UNASSESSED,.k-NONE,.k-UNCHANGED{border-left-color:#475467}.k-EFFECTIVE,.k-FULL,.k-IMPROVED{border-left-color:#067647}.k-INFORMATIONAL{border-left-color:#175cd3}
.narrative-gap{background:#fff4e5;border-left:5px solid #b54708;padding:8px 10px;border-radius:6px;font-weight:650}
.now-list{margin:4px 0 8px;padding-left:20px}
.plan{margin:16px 0;background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px}
.plan h2{margin:0 0 6px;font-size:20px}.plan-list{padding-left:22px;margin:12px 0}
.plan-item{margin:0 0 12px;padding:10px 12px;border:1px solid var(--line);border-radius:10px}
.plan-head{font-size:15px}.plan-meta{font-size:12px;margin:4px 0}
.prio{display:inline-block;border:2px solid #475467;border-radius:6px;padding:0 6px;font-weight:700;font-size:12px;margin-right:4px}
.p-P0{border-color:#b42318;color:#b42318}.p-P1{border-color:#b54708;color:#b54708}.p-P2{border-color:#5925dc;color:#5925dc}
.plan-checks{margin:6px 0;padding-left:18px}.plan-checks li{margin:5px 0;overflow-wrap:anywhere}
.plan-others{font-size:12px;overflow-wrap:anywhere}
.plan-howto{background:#f8fafc;border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin-top:8px}
.plan-howto h3{margin:0 0 6px;font-size:14px}
@media print{.plan-item,.plan-howto{break-inside:avoid}}
"""


def _kpis(counts: dict[str, Any], locale: str) -> str:
    labels = STATUS_LABELS[locale]
    return '<span class="kpis">' + "".join(
        f'<span class="kpi k-{esc(key)}" title="{esc(key)}:{esc(value)}"><b>{esc(value)}</b> {esc(labels.get(key, key))}</span>'
        for key, value in counts.items()
    ) + "</span>"


def narrative_html(document: dict[str, Any], locale: str) -> str:
    t = TEXT[locale]
    meta = document["metadata"]
    assurance = document["assurance"]
    now = document["roadmap"]["NOW"]
    scenarios = document["securityScenarios"]
    comparison = document["comparison"]
    cards = {row["id"]: row for row in document["actionCards"]}
    confirmations = list(dict.fromkeys(row["attackConfirmation"] for row in scenarios))
    partial = assurance["evidenceCoverage"].get("PARTIAL")
    unassessed = assurance["controlOutcomes"].get("UNASSESSED")
    total = len(document["controlAssessments"])
    parts = [
        f'<p>{esc(t["narrativeRun"].format(run=meta["runId"], n=total))}</p>{_kpis(assurance["controlOutcomes"], locale)}',
        f'<p class="narrative-gap">{esc(t["narrativeGap"].format(u=unassessed, n=total))}</p>' if unassessed else "",
        f'<p>{esc(t["narrativeCoverage"])}</p>{_kpis(assurance["evidenceCoverage"], locale)}'
        + (f'<p><span class="narrative-partial">{esc(t["narrativePartial"].format(k=partial))}</span></p>' if partial else ""),
        (f'<p>{esc(t["narrativeNow"].format(n=len(now)))}</p><ul class="now-list">'
         + "".join(f'<li><b>{esc(row["actionCardId"])}</b> · {esc(cards.get(row["actionCardId"], {}).get("title"))}</li>' for row in now)
         + "</ul>") if now else f'<p>{esc(t["narrativeNowEmpty"])}</p>',
        f'<p>{esc(t["narrativeScenarios"].format(n=len(scenarios)))} {badges(confirmations)} {esc(t["narrativeNoAttack"])}</p>',
        (f'<p>{esc(t["narrativeNoBaseline"])}</p>' if comparison is None else
         f'<p>{esc(t["narrativeComparison"].format(run=comparison["baselineRunId"]))}</p>{_kpis(comparison["summary"], locale)}'),
        f'<p class="muted">{esc(t["narrativeSource"])}</p>',
    ]
    return (
        f'<section class="notice narrative" id="executive-narrative" aria-label="{esc(t["narrativeTitle"])}">'
        f'<h2>{esc(t["narrativeTitle"])}</h2>{"".join(parts)}</section>'
    )


def action_plan_html(document: dict[str, Any], locale: str) -> str:
    t = TEXT[locale]
    labels = STATUS_LABELS[locale]
    now = document["roadmap"]["NOW"]
    cards = {row["id"]: row for row in document["actionCards"]}
    outcomes = {row["checkId"]: row["outcome"] for row in document["controlAssessments"]}
    statements = {row["checkId"]: row["statement"] for row in document["traceability"]["observations"]}
    shown = ("INEFFECTIVE", "AT_RISK")
    playbooks = [(tuple(cards.get(row["actionCardId"], {}).get("actions", [])),
                  tuple(cards.get(row["actionCardId"], {}).get("closureEvidence", []))) for row in now]
    shared = bool(playbooks) and len(set(playbooks)) == 1

    def howto(actions: Iterable[Any], closure: Iterable[Any]) -> str:
        return (f'<div class="plan-howto"><h3>{esc(t["planHowTo"])}</h3>{ul(actions)}'
                f'<h3>{esc(t["planClosure"])}</h3>{ul(closure)}</div>')

    items = []
    for row in now:
        card = cards.get(row["actionCardId"], {})
        failing = [cid for cid in row["controlIds"] if outcomes.get(cid) in shown]
        others = [cid for cid in row["controlIds"] if outcomes.get(cid) not in shown]
        checks = "".join(
            f'<li><span class="kpi k-{esc(outcomes[cid])}" title="{esc(outcomes[cid])}">{esc(labels.get(outcomes[cid], outcomes[cid]))}</span> '
            f'<b>{esc(cid)}</b> - {esc(statements.get(cid))}</li>'
            for cid in failing
        ) or f'<li class="muted">{esc(t["planNoFailing"])}</li>'
        other_html = (f'<div class="plan-others muted">{esc(t["planOthers"])} {esc(", ".join(others))}</div>' if others else "")
        items.append(
            f'<li class="plan-item" data-plan-card="{esc(row["actionCardId"])}">'
            f'<div class="plan-head"><span class="prio p-{esc(row["priority"])}">{esc(row["priority"])}</span> '
            f'<strong>{esc(row["actionCardId"])} · {esc(card.get("title"))}</strong></div>'
            f'<div class="plan-meta muted">{esc(t["planOwners"])}: {esc(", ".join(row["owners"]))} · '
            f'{esc(t["planDue"])}: {esc(row["dueInDays"])} {esc(t["planDays"])}</div>'
            f'<ul class="plan-checks">{checks}</ul>{other_html}'
            + ("" if shared else howto(card.get("actions", []), card.get("closureEvidence", [])))
            + "</li>"
        )
    body = (f'<ol class="plan-list">{"".join(items)}</ol>' if items else f'<p class="muted">{esc(t["planEmpty"])}</p>')
    common = howto(playbooks[0][0], playbooks[0][1]) if shared else ""
    return (
        f'<section class="plan" id="action-plan" aria-label="{esc(t["planTitle"])}">'
        f'<h2>{esc(t["planTitle"])}</h2><p class="muted">{esc(t["planIntro"])}</p>{body}{common}</section>'
    )


_render_without_action_plan = render


def render(document, locale):
    html_text = _render_without_action_plan(document, locale)
    start = html_text.find('id="executive-narrative"')
    end = html_text.find("</section>", start) if start >= 0 else -1
    if start < 0 or end < 0 or "</style>" not in html_text:
        raise ValueError("executive narrative anchor for the action plan not found")
    end += len("</section>")
    html_text = html_text[:end] + action_plan_html(document, locale) + html_text[end:]
    return html_text.replace("</style>", PLAN_CSS + "</style>", 1)



# --- Evidence trace per failing check (render-only, MSRC-style structure) -----
TEXT["en-US"].update({
    "traceTitle": "Evidence trace",
    "traceClass": "Class / severity", "traceEnv": "Environment", "traceCollected": "collected at",
    "traceEvidence": "Evidence sources", "traceIntegrity": "Integrity / source status", "traceDigest": "Content digest",
    "traceDetail": "Collection detail", "traceExpected": "Expected (claim)", "traceVerdict": "Verdict / confidence",
    "traceReasons": "Reason codes", "traceAbsence": "If evidence is absent", "traceFields": "Required fields",
    "traceMissing": "Missing fields", "traceNone": "none",
    "traceResources": "Per-resource list", "traceResourcesHint": "open in the collection package",
    "traceResourcesNone": "not listed in the canonical contract",
    "traceReproduce": "How to reproduce",
    "traceReproduceText": "Open collection package {pkg}, read the files listed above and confirm the resources in the Azure portal. For a per-resource view with portal links, load the same package in the legacy report (step 3).",
})
TEXT["pt-BR"].update({
    "traceTitle": "Rastro da evidência",
    "traceClass": "Classe / severidade", "traceEnv": "Ambiente", "traceCollected": "coletado em",
    "traceEvidence": "Fontes da evidência", "traceIntegrity": "Integridade / status da fonte", "traceDigest": "Digest do conteúdo",
    "traceDetail": "Detalhe da coleta", "traceExpected": "Esperado (claim)", "traceVerdict": "Veredito / confiança",
    "traceReasons": "Códigos de motivo", "traceAbsence": "Se a evidência estiver ausente", "traceFields": "Campos exigidos",
    "traceMissing": "Campos ausentes", "traceNone": "nenhum",
    "traceResources": "Lista por recurso", "traceResourcesHint": "abrir no pacote da coleta",
    "traceResourcesNone": "não listada no contrato canônico",
    "traceReproduce": "Como reproduzir",
    "traceReproduceText": "Abra o pacote da coleta {pkg}, leia os arquivos listados acima e confirme os recursos no portal do Azure. Para a visão por recurso com links do portal, carregue o mesmo pacote no relatório legado (etapa 3).",
})

TRACE_CSS = r"""
.trace{margin:4px 0 8px 2px;border:1px dashed var(--line);border-radius:8px;background:#fbfcfe}
.trace summary{cursor:pointer;padding:6px 10px;font-size:12px;font-weight:650;color:#0f6cbd}
.trace .inside{padding:6px 10px 10px}
.trace dl{display:grid;grid-template-columns:minmax(120px,190px) minmax(0,1fr);gap:4px 12px;margin:0;font-size:12px}
.trace dt{color:var(--muted)}.trace dd{margin:0;overflow-wrap:anywhere}
.trace .mono{font-size:11px}.trace .miss{color:#b42318;font-weight:650}
@media(max-width:900px){.trace dl{grid-template-columns:1fr}}
"""


def _plain_list(values: Iterable[Any]) -> str:
    return ", ".join(esc(value) for value in values)


def evidence_trace_html(check_id: str, evidence: dict[str, Any], observation: dict[str, Any],
                        claim: dict[str, Any], package: Any, locale: str) -> str:
    t = TEXT[locale]
    sources = list(evidence.get("sources") or [])
    findings = [source for source in sources if str(source).startswith("findings/")]
    missing = list(evidence.get("missingFields") or [])
    reasons = claim.get("reasonCodes") or []
    rows = [
        (t["traceClass"], f'{esc(observation.get("kind"))} · {esc(observation.get("severity"))}'),
        (t["traceEnv"], f'{esc(evidence.get("scope"))} · {esc(t["traceCollected"])} <span class="mono">{esc(evidence.get("collectedAt"))}</span>'),
        (t["traceEvidence"], f'<span class="mono">{_plain_list(sources)}</span>'),
        (t["traceIntegrity"], f'{esc(evidence.get("integrity"))} · {esc(evidence.get("sourceStatus"))}'),
        (t["traceDigest"], f'<span class="mono">{esc(evidence.get("contentDigest"))}</span>'),
        (t["traceDetail"], esc(evidence.get("detail"))),
        (t["traceExpected"], esc(claim.get("assertion"))),
        (t["traceVerdict"], f'{esc(claim.get("verdict"))} · {esc(claim.get("confidence"))}'),
        (t["traceReasons"], f'<span class="mono">{_plain_list(reasons) if isinstance(reasons, list) else esc(reasons)}</span>'),
        (t["traceAbsence"], esc(claim.get("absenceMeans"))),
        (t["traceFields"], f'<span class="mono">{_plain_list(evidence.get("requiredFields") or []) or esc(t["traceNone"])}</span>'),
        (t["traceMissing"], (f'<span class="mono miss">{_plain_list(missing)}</span>' if missing else esc(t["traceNone"]))),
        (t["traceResources"], (f'<span class="mono">{_plain_list(findings)}</span> ({esc(t["traceResourcesHint"])})'
                               if findings else esc(t["traceResourcesNone"]))),
        (t["traceReproduce"], esc(t["traceReproduceText"].format(pkg=package))),
    ]
    body = "".join(f"<dt>{esc(label)}</dt><dd>{value}</dd>" for label, value in rows)
    return (f'<details class="trace" data-trace="{esc(check_id)}"><summary>{esc(t["traceTitle"])} · {esc(check_id)}</summary>'
            f'<div class="inside"><dl>{body}</dl></div></details>')


def action_plan_html(document: dict[str, Any], locale: str) -> str:
    t = TEXT[locale]
    labels = STATUS_LABELS[locale]
    now = document["roadmap"]["NOW"]
    cards = {row["id"]: row for row in document["actionCards"]}
    outcomes = {row["checkId"]: row["outcome"] for row in document["controlAssessments"]}
    observations = {row["checkId"]: row for row in document["traceability"]["observations"]}
    claims = {row["checkId"]: row for row in document["traceability"]["claims"]}
    evidence = {row["checkId"]: row for row in document["traceability"]["evidence"]}
    package = document["metadata"]["source"]["name"]
    shown = ("INEFFECTIVE", "AT_RISK")
    playbooks = [(tuple(cards.get(row["actionCardId"], {}).get("actions", [])),
                  tuple(cards.get(row["actionCardId"], {}).get("closureEvidence", []))) for row in now]
    shared = bool(playbooks) and len(set(playbooks)) == 1

    def howto(actions: Iterable[Any], closure: Iterable[Any]) -> str:
        return (f'<div class="plan-howto"><h3>{esc(t["planHowTo"])}</h3>{ul(actions)}'
                f'<h3>{esc(t["planClosure"])}</h3>{ul(closure)}</div>')

    items = []
    for row in now:
        card = cards.get(row["actionCardId"], {})
        failing = [cid for cid in row["controlIds"] if outcomes.get(cid) in shown]
        others = [cid for cid in row["controlIds"] if outcomes.get(cid) not in shown]
        checks = "".join(
            f'<li><span class="kpi k-{esc(outcomes[cid])}" title="{esc(outcomes[cid])}">{esc(labels.get(outcomes[cid], outcomes[cid]))}</span> '
            f'<b>{esc(cid)}</b> - {esc(observations.get(cid, {}).get("statement"))}'
            + evidence_trace_html(cid, evidence.get(cid, {}), observations.get(cid, {}), claims.get(cid, {}), package, locale)
            + "</li>"
            for cid in failing
        ) or f'<li class="muted">{esc(t["planNoFailing"])}</li>'
        other_html = (f'<div class="plan-others muted">{esc(t["planOthers"])} {esc(", ".join(others))}</div>' if others else "")
        items.append(
            f'<li class="plan-item" data-plan-card="{esc(row["actionCardId"])}">'
            f'<div class="plan-head"><span class="prio p-{esc(row["priority"])}">{esc(row["priority"])}</span> '
            f'<strong>{esc(row["actionCardId"])} · {esc(card.get("title"))}</strong></div>'
            f'<div class="plan-meta muted">{esc(t["planOwners"])}: {esc(", ".join(row["owners"]))} · '
            f'{esc(t["planDue"])}: {esc(row["dueInDays"])} {esc(t["planDays"])}</div>'
            f'<ul class="plan-checks">{checks}</ul>{other_html}'
            + ("" if shared else howto(card.get("actions", []), card.get("closureEvidence", [])))
            + "</li>"
        )
    body = (f'<ol class="plan-list">{"".join(items)}</ol>' if items else f'<p class="muted">{esc(t["planEmpty"])}</p>')
    common = howto(playbooks[0][0], playbooks[0][1]) if shared else ""
    return (
        f'<section class="plan" id="action-plan" aria-label="{esc(t["planTitle"])}">'
        f'<h2>{esc(t["planTitle"])}</h2><p class="muted">{esc(t["planIntro"])}</p>{body}{common}</section>'
    )


_render_without_evidence_trace = render


def render(document, locale):
    html_text = _render_without_evidence_trace(document, locale)
    if "</style>" not in html_text:
        raise ValueError("report has no style block")
    return html_text.replace("</style>", TRACE_CSS + "</style>", 1)



# --- Optional resource index (sidecar bound by runId) -> Azure portal links ---
_RESOURCE_INDEX: dict[str, Any] | None = None
_RENDER_RUN_ID: Any = None
TEXT["en-US"].update({
    "traceLinks": "Resources (Azure portal)",
    "traceUnbound": "Resource index ignored: its runId does not match this report.",
    "traceBinding": "Index binding",
    "traceFirst": "Showing the first {n} rows; the full list is in {file}.",
    "traceNoRows": "no rows for this check in the index",
})
TEXT["pt-BR"].update({
    "traceLinks": "Recursos (portal do Azure)",
    "traceUnbound": "Índice de recursos ignorado: o runId não corresponde a este relatório.",
    "traceBinding": "Vínculo do índice",
    "traceFirst": "Mostrando as primeiras {n} linhas; a lista completa está em {file}.",
    "traceNoRows": "nenhuma linha para este check no índice",
})
RESOURCE_CSS = r"""
.trace .res{margin:0;padding-left:16px}.trace .res li{margin:2px 0;overflow-wrap:anywhere}
.trace .res a{color:#0f6cbd;font-weight:650}.trace .res .attrs{font-size:11px;color:var(--muted)}
"""
_RESOURCE_LIMIT = 25


def _resource_block(check_id: str, locale: str) -> str:
    t = TEXT[locale]
    index = _RESOURCE_INDEX
    if index is None:
        return ""
    if index.get("runId") != _RENDER_RUN_ID:
        return f'<dt>{esc(t["traceLinks"])}</dt><dd><span class="miss" data-resource-index="unbound">{esc(t["traceUnbound"])}</span></dd>'
    rows = (index.get("checks") or {}).get(check_id)
    if not rows:
        return f'<dt>{esc(t["traceLinks"])}</dt><dd class="muted">{esc(t["traceNoRows"])}</dd>'
    items = []
    for row in rows[:_RESOURCE_LIMIT]:
        attrs = "; ".join(f"{key}={value}" for key, value in (row.get("attributes") or {}).items() if value)
        label = (f'<a href="{esc(row["portalUrl"])}" target="_blank" rel="noopener noreferrer">{esc(row.get("label"))}</a>'
                 if row.get("portalUrl") else esc(row.get("label")))
        items.append(f'<li>{label} <span class="muted">({esc(row.get("kind"))})</span><br><span class="attrs">{esc(attrs)}</span></li>')
    more = (f'<div class="muted">{esc(t["traceFirst"].format(n=_RESOURCE_LIMIT, file=f"findings/{check_id}.csv"))}</div>'
            if rows[_RESOURCE_LIMIT:] else "")
    binding = f'<div class="muted">{esc(t["traceBinding"])}: {esc(index.get("binding"))} · sha256 {esc(index.get("packageSha256"))}</div>'
    return f'<dt>{esc(t["traceLinks"])}</dt><dd data-resource-index="{esc(check_id)}"><ul class="res">{"".join(items)}</ul>{more}{binding}</dd>'


_trace_without_resources = evidence_trace_html


def evidence_trace_html(check_id, evidence, observation, claim, package, locale):
    html_text = _trace_without_resources(check_id, evidence, observation, claim, package, locale)
    block = _resource_block(check_id, locale)
    return html_text.replace("</dl>", block + "</dl>", 1) if block else html_text


_render_without_resources = render


def render(document, locale):
    global _RENDER_RUN_ID
    _RENDER_RUN_ID = document["metadata"]["runId"]
    html_text = _render_without_resources(document, locale)
    return html_text.replace("</style>", RESOURCE_CSS + "</style>", 1) if _RESOURCE_INDEX is not None else html_text


_main_without_resources = main


def main() -> int:
    global _RESOURCE_INDEX
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--resources", type=Path)
    known, rest = pre.parse_known_args()
    if known.resources:
        index = json.loads(known.resources.read_text(encoding="utf-8-sig"))
        if index.get("contract") != "resource-index.v4" or not isinstance(index.get("checks"), dict):
            raise SystemExit("invalid resource index: expected contract resource-index.v4")
        _RESOURCE_INDEX = index
    sys.argv = [sys.argv[0], *rest]
    return _main_without_resources()


if __name__ == "__main__":
    raise SystemExit(main())
