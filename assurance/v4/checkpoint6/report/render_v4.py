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
:root{--bg:#f4f6fa;--paper:#fff;--ink:#1f2a3d;--muted:#5d6a7e;--line:#e1e7f0;--line-2:#cfd8e6;--blue:#1b6ab0;--accent:#1b6ab0;--nav:#1f3050;--navy:#1f3050;--soft:#eaf1f9;--panel:#f6f8fc;--good:#2b6a49;--warn:#7a5316;--bad:#8a3737;--violet:#40508a;--shadow:0 1px 2px #1f305008,0 4px 16px #1f30500d}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 "Segoe UI",Arial,sans-serif}a{color:inherit}.shell{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:100vh}.side{position:sticky;top:0;height:100vh;background:var(--nav);color:#fff;padding:24px 18px;overflow:auto}.brand{font-size:19px;font-weight:700}.brand small{display:block;color:#9ecbee;font-size:12px;font-weight:500;margin-top:4px}.side nav{display:grid;gap:3px;margin-top:22px}.side nav a{text-decoration:none;padding:8px 10px;border-radius:7px;color:#d7e6f5}.side nav a:hover,.side nav a.active{background:#173b5c;color:#fff}.main{min-width:0;padding:28px}.hero{background:linear-gradient(135deg,#092846,#0f6cbd);color:#fff;border-radius:16px;padding:28px;box-shadow:0 12px 30px #0b31551c}.hero h1{margin:0 0 5px;font-size:30px}.hero p{margin:0;color:#cfe8fb}.meta{display:flex;flex-wrap:wrap;gap:9px;margin-top:18px}.meta span,.badge{display:inline-flex;align-items:center;border-radius:999px;padding:4px 9px;background:#eaf2fb;color:#123b60;font-size:12px;font-weight:650}.hero .meta span{background:#ffffff1e;color:#fff;border:1px solid #ffffff2e}.toolbar{display:flex;gap:8px;margin:16px 0}.btn{border:1px solid var(--line);background:#fff;border-radius:8px;padding:8px 12px;font-weight:650;cursor:pointer}.section{scroll-margin-top:12px;margin:18px 0;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:20px;box-shadow:0 6px 18px #23344d0a}.section h2{margin:0 0 14px;font-size:22px}.section h3{margin:18px 0 9px;font-size:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:11px}.card{border:1px solid var(--line);border-radius:11px;padding:14px;min-width:0}.card h3,.card h4{margin:0 0 8px}.metric strong{display:block;font-size:25px;color:var(--blue)}.muted{color:var(--muted)}.mono{font:12px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:10px}table{border-collapse:collapse;width:100%;min-width:720px}th,td{border-bottom:1px solid var(--line);padding:9px 10px;text-align:left;vertical-align:top}th{background:#f7f9fc;color:#41546b;position:sticky;top:0}tr:last-child td{border-bottom:0}.pillset{display:flex;flex-wrap:wrap;gap:5px}.badge{background:#edf2f7;color:#34465b}.badge.P0,.badge.CRITICAL,.badge.INEFFECTIVE,.badge.GAP,.badge.REGRESSED{background:#fee4e2;color:var(--bad)}.badge.P1,.badge.HIGH,.badge.AT_RISK,.badge.DEGRADED,.badge.PARTIALLY_SUPPORTED{background:#fff1d6;color:var(--warn)}.badge.P2,.badge.MEDIUM,.badge.UNKNOWN,.badge.UNASSESSED,.badge.POTENTIAL_RELEVANCE{background:#f2eaff;color:var(--violet)}.badge.P3,.badge.MINIMAL,.badge.LOW,.badge.EFFECTIVE,.badge.SUPPORTED,.badge.VALIDATED,.badge.IMPROVED{background:#dcfae6;color:var(--good)}.badge.HYPOTHESIS,.badge.NOT_COVERED,.badge.NONE{background:#eef2f6;color:#586b80}.badge.PROVIDER_IDENTIFIED,.badge.FULL{background:#e0f2fe;color:#075985}.path{display:grid;grid-template-columns:repeat(7,minmax(70px,1fr));align-items:center;gap:6px;margin:12px 0}.node{border:1px solid #b9d4ec;background:#edf6fd;color:#164b76;padding:10px 7px;text-align:center;border-radius:9px;font-weight:700}.arrow{text-align:center;color:#7991a8;font-size:19px}.scenario{margin:12px 0;border:1px solid var(--line);border-radius:11px;overflow:hidden}.scenario summary{cursor:pointer;padding:13px 15px;background:#f8fafc;font-weight:700}.scenario .inside{padding:15px}.columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px}.notice{padding:14px;border-left:4px solid var(--blue);background:#eef7ff;border-radius:7px}.kv{display:grid;grid-template-columns:minmax(130px,190px) minmax(0,1fr);gap:5px 14px}.kv dt{color:var(--muted)}.kv dd{margin:0;overflow-wrap:anywhere}ul.compact{margin:6px 0;padding-left:19px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f6fb;color:#1f2a3d;border:1px solid var(--line);padding:12px;border-radius:8px}.footer{color:var(--muted);text-align:center;padding:18px;overflow-wrap:anywhere}.only-print{display:none}
@media(max-width:900px){.shell{display:block}.side{position:static;height:auto}.side nav{display:flex;overflow:auto}.side nav a{white-space:nowrap}.main{padding:14px}.columns{grid-template-columns:1fr}.path{grid-template-columns:1fr}.arrow{transform:rotate(90deg)}.hero{padding:20px}.kv{grid-template-columns:1fr}.kv dd{margin-bottom:7px}}
@media print{body{background:#fff;font-size:10px}.shell{display:block}.side,.toolbar{display:none}.main{padding:0}.hero{box-shadow:none;border-radius:0;print-color-adjust:exact}.section{box-shadow:none;break-inside:avoid;margin:8mm 0}.only-print{display:block}details>.inside{display:block!important}details{break-inside:avoid}table{min-width:0}th{position:static}@page{size:landscape;margin:8mm}}
"""

JS = r"""'use strict';
(function(){
  const doc=document,body=doc.body;
  const links=[...doc.querySelectorAll('.side nav a')];
  const pairs=links.map(a=>[a,doc.querySelector(a.getAttribute('href'))]).filter(p=>p[1]).sort((x,y)=>(x[1].compareDocumentPosition(y[1])&4)?-1:1);
  const sections=pairs.map(p=>p[1]);
  const label=doc.getElementById('curlabel'),totop=doc.getElementById('totop');
  const activate=()=>{
    if(!sections.length)return;
    let current=sections[0];
    for(const section of sections){if(section.getBoundingClientRect().top<=110)current=section;}
    links.forEach(a=>{
      const on=a.getAttribute('href')==='#'+current.id;
      a.classList.toggle('active',on);
      if(on&&label){const l=a.querySelector('.nl');label.textContent=l?l.textContent:'';}
    });
    if(totop)totop.classList.toggle('show',scrollY>600);
  };
  addEventListener('scroll',activate,{passive:true});activate();
  const toggle=doc.getElementById('navtoggle'),veil=doc.getElementById('navveil');
  if(toggle)toggle.addEventListener('click',()=>body.classList.toggle('navopen'));
  if(veil)veil.addEventListener('click',()=>body.classList.remove('navopen'));
  links.forEach(a=>a.addEventListener('click',()=>body.classList.remove('navopen')));
  if(totop)totop.addEventListener('click',()=>scrollTo({top:0,behavior:'smooth'}));
  const notice=doc.getElementById('validation-notice');
  if(notice)notice.addEventListener('click',()=>notice.classList.toggle('open'));
  doc.getElementById('print').addEventListener('click',()=>print());
  doc.getElementById('expand').addEventListener('click',()=>doc.querySelectorAll('details').forEach(x=>x.open=true));
  doc.getElementById('collapse').addEventListener('click',()=>doc.querySelectorAll('details').forEach(x=>x.open=false));
  const rows=[...doc.querySelectorAll('#checks tbody tr')],input=doc.getElementById('chkfilter'),chips=[...doc.querySelectorAll('[data-filter]')],count=doc.getElementById('chkcount');
  let mode='ALL';
  const apply=()=>{
    const q=(input?input.value:'').trim().toLowerCase();let n=0;
    rows.forEach(r=>{const ok=(mode==='ALL'||r.dataset.o===mode)&&(!q||r.textContent.toLowerCase().includes(q));r.hidden=!ok;if(ok)n++;});
    if(count)count.textContent=n;
  };
  if(input)input.addEventListener('input',apply);
  chips.forEach(c=>c.addEventListener('click',()=>{mode=c.dataset.filter;chips.forEach(x=>x.classList.toggle('on',x===c));apply();}));
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
.badge{border:1px solid transparent;font-weight:600;letter-spacing:.01em;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.badge.P0,.badge.CRITICAL,.badge.INEFFECTIVE,.badge.GAP,.badge.REGRESSED,.badge.FAIL,.badge.REFUTED,.badge[class*=" INEFFECTIVE:"],.badge[class*=" GAP:"]{background:#f9ecec;color:#8a3737;border-color:#efd0d0}
.badge.P1,.badge.HIGH,.badge.AT_RISK,.badge.DEGRADED,.badge.PARTIALLY_SUPPORTED,.badge.WARN,.badge.ELEVATED,.badge.WEAKNESS_INDICATED,.badge[class*=" AT_RISK:"],.badge[class*=" DEGRADED:"]{background:#fbf1de;color:#7a5316;border-color:#f0dcb4}
.badge.P2,.badge.MEDIUM,.badge.UNKNOWN,.badge.UNASSESSED,.badge.POTENTIAL_RELEVANCE,.badge.UNRESOLVED,.badge.PARTIAL,.badge.OPEN,.badge.TODO,.badge.EXPOSURE_INDICATED,.badge.NOT_EVALUABLE,.badge[class*=" UNASSESSED:"],.badge[class*=" UNKNOWN:"]{background:#eceffa;color:#40508a;border-color:#d6dcf0}
.badge.P3,.badge.MINIMAL,.badge.LOW,.badge.EFFECTIVE,.badge.SUPPORTED,.badge.VALIDATED,.badge.IMPROVED,.badge.PASS,.badge.VERIFIED,.badge.MITIGATED,.badge.NOT_INDICATED,.badge[class*=" EFFECTIVE:"]{background:#e7f3ec;color:#2b6a49;border-color:#cbe3d4}
.badge.INFO,.badge.INFORMATIONAL,.badge.NOT_ASSERTED,.badge.N\/A,.badge.NOW,.badge.PROVIDER_IDENTIFIED,.badge.FULL,.badge[class*=" INFORMATIONAL:"]{background:#e6f0fa;color:#265f96;border-color:#cfe1f3}
.badge.HYPOTHESIS,.badge.NOT_COVERED,.badge.NONE,.badge.UNCHANGED,.badge[class*=" NOT_COVERED:"]{background:#eef1f5;color:#4b586a;border-color:#dde2ea}
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
.badge[class*=" FULL:"]{background:#e6f0fa;color:#265f96;border-color:#cfe1f3}.badge[class*=" PARTIAL:"]{background:#eceffa;color:#40508a;border-color:#d6dcf0}.badge[class*=" NONE:"]{background:#eef1f5;color:#4b586a;border-color:#dde2ea}
.badge[class*=" IMPROVED:"]{background:#e7f3ec;color:#2b6a49;border-color:#cbe3d4}.badge[class*=" REGRESSED:"]{background:#f9ecec;color:#8a3737;border-color:#efd0d0}.badge[class*=" UNCHANGED:"]{background:#eef1f5;color:#4b586a;border-color:#dde2ea}
@media print{.narrative{break-inside:avoid}}
"""


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
.kpi{display:inline-flex;align-items:baseline;gap:6px;border-radius:999px;padding:1px 10px;font-size:12px;font-weight:600;background:#eef1f5;color:#4b586a;border:1px solid #dde2ea;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.kpi b{font-size:18px}
.k-INEFFECTIVE,.k-REGRESSED{background:#f9ecec;color:#8a3737;border-color:#efd0d0}.k-AT_RISK,.k-PARTIAL{background:#fbf1de;color:#7a5316;border-color:#f0dcb4}
.k-EFFECTIVE,.k-FULL,.k-IMPROVED{background:#e7f3ec;color:#2b6a49;border-color:#cbe3d4}.k-INFORMATIONAL{background:#e6f0fa;color:#265f96;border-color:#cfe1f3}
.narrative-gap{background:#fbf1de;border-left:3px solid #d9b35f;padding:8px 12px;border-radius:6px;font-weight:600}
.now-list{margin:4px 0 8px;padding-left:20px}
.plan{margin:16px 0;background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px}
.plan h2{margin:0 0 6px;font-size:20px}.plan-list{padding-left:22px;margin:12px 0}
.plan-item{margin:0 0 12px;padding:10px 12px;border:1px solid var(--line);border-radius:10px}
.plan-head{font-size:15px}.plan-meta{font-size:12px;margin:4px 0}
.prio{display:inline-block;border:1px solid #dde2ea;background:#eef1f5;color:#4b586a;border-radius:6px;padding:1px 8px;font-weight:650;font-size:12px;margin-right:4px}
.p-P0{background:#f9ecec;border-color:#efd0d0;color:#8a3737}.p-P1{background:#fbf1de;border-color:#f0dcb4;color:#7a5316}.p-P2{background:#eceffa;border-color:#d6dcf0;color:#40508a}
.plan-checks{margin:6px 0;padding-left:18px}.plan-checks li{margin:5px 0;overflow-wrap:anywhere}
.plan-others{font-size:12px;overflow-wrap:anywhere}
.plan-howto{background:#f8fafc;border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin-top:8px}
.plan-howto h3{margin:0 0 6px;font-size:14px}
@media print{.plan-item,.plan-howto{break-inside:avoid}}
"""


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
.trace summary{cursor:pointer;padding:6px 10px;font-size:12px;font-weight:650;color:var(--accent)}
.trace .inside{padding:6px 10px 10px}
.trace dl{display:grid;grid-template-columns:minmax(120px,190px) minmax(0,1fr);gap:4px 12px;margin:0;font-size:12px}
.trace dt{color:var(--muted)}.trace dd{margin:0;overflow-wrap:anywhere}
.trace .mono{font-size:11px}.trace .miss{color:#8a3737;font-weight:650}
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
.trace .res a{color:var(--accent);font-weight:650}.trace .res .attrs{font-size:11px;color:var(--muted)}
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

# --- PR10-RESOURCE-COVERAGE: per-machine links for aggregate findings + inferred marker ---
_RELATED_PORTAL = "https://portal.azure.com/#@/resource/subscriptions/"


def _related_block(check_id, portuguese=False):
    from html import escape as _esc
    index = globals().get("_RESOURCE_INDEX")
    if not isinstance(index, dict) or not check_id:
        return ""
    checks = index.get("checks", index)
    rows = checks.get(check_id) if isinstance(checks, dict) else None
    if not isinstance(rows, list):
        return ""
    links: dict[str, str] = {}
    inferred = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("kind") in ("inferred", "resourceGroup-inferred"):
            inferred += 1
        for item in row.get("relatedResources") or []:
            url = str((item or {}).get("portalUrl") or "")
            if url.startswith(_RELATED_PORTAL):
                links.setdefault(str(item.get("label") or url), url)
    parts = []
    if links:
        shown = sorted(links.items())[:25]
        anchors = ", ".join(f'<a href="{_esc(url)}" target="_blank" rel="noopener noreferrer">{_esc(label)}</a>' for label, url in shown)
        more = len(links) - len(shown)
        tail = (f" (+{more})" if more > 0 else "")
        title = "Máquinas afetadas (portal Azure):" if portuguese else "Affected machines (Azure portal):"
        parts.append(f'<p class="trace-related" data-related-machines="{len(links)}"><strong>{title}</strong> {anchors}{tail}</p>')
    if inferred:
        note = ("linha(s) com link inferido (assinatura única do pacote; validar no portal)" if portuguese
                else "row(s) with inferred link (single subscription in package; verify in portal)")
        parts.append(f'<p class="trace-related" data-inferred-rows="{inferred}">{inferred} {note}</p>')
    return "".join(parts)


_resource_block_v10 = _resource_block


def _resource_block(*args, **kwargs):
    import re as _re
    out = _resource_block_v10(*args, **kwargs)
    if not out or 'data-resource-index="unbound"' in out:
        return out
    values = list(args) + list(kwargs.values())
    check_id = next((v for v in values if isinstance(v, str) and _re.fullmatch(r"CHK-\d+", v)), None)
    if check_id is None:
        check_id = next((v.get("checkId") for v in values if isinstance(v, dict) and v.get("checkId")), None)
    portuguese = ("Recursos" in out) or ("recursos" in out)
    return out + _related_block(check_id, portuguese)

# --- PR17-NAVIGATION: toolbar in the sidebar; Comparison only when a baseline exists (render-only) ---
TEXT["en-US"]["noBaseline"] = "No baseline was supplied: single collection, so there is no before/after comparison. Run the evaluation with --baseline <previous package> to compare."
TEXT["pt-BR"]["noBaseline"] = "Nenhum baseline foi fornecido: coleta única, portanto sem comparação antes/depois. Rode a avaliação com --baseline <pacote anterior> para comparar."
NAV17_CSS = r"""
.side .toolbar{display:grid;gap:6px;margin:18px 0 0;padding:0;background:none;border:0;box-shadow:none;position:static}
.side .toolbar .btn{width:100%;text-align:left;background:#173b5c;color:#fff;border:1px solid #2b5378;border-radius:7px;padding:8px 10px;cursor:pointer}
#comparison-null{margin:0 0 12px}
@media(max-width:900px){.side .toolbar{display:flex;flex-wrap:wrap}.side .toolbar .btn{width:auto}}
"""

_render_without_nav17 = render


def render(document, locale):
    import re as _re
    html_text = _render_without_nav17(document, locale)
    anchor = '<div class="toolbar">'
    if html_text.count(anchor) != 1 or html_text.count("</nav></aside>") != 1 or "</style>" not in html_text:
        raise ValueError("report layout anchors for the sidebar toolbar not found")
    start = html_text.index(anchor)
    toolbar = html_text[start:html_text.index("</div>", start) + len("</div>")]
    html_text = html_text.replace(toolbar, "", 1).replace("</nav></aside>", "</nav>" + toolbar + "</aside>", 1)
    if document["comparison"] is None:
        section = _re.search(r'<section class="section" id="comparison">.*?</section>', html_text, _re.S)
        note = _re.search(r'<p class="notice" id="comparison-null">.*?</p>', section.group(0), _re.S) if section else None
        overview = _re.search(r'<section class="section" id="overview"><h2>[^<]*</h2>', html_text)
        if not (section and note and overview):
            raise ValueError("report layout anchors for the null comparison not found")
        html_text = html_text.replace(section.group(0), "", 1)
        html_text = _re.sub(r'<a href="#comparison">[^<]*</a>', "", html_text, count=1)
        html_text = html_text.replace(overview.group(0), overview.group(0) + note.group(0), 1)
    return html_text.replace("</style>", NAV17_CSS + "</style>", 1)

# --- PR18-LINKS: CHK pills link to the Checks table; compact Zero Trust x Tier view (render-only post-processing) ---
LINKS18_CSS = r"""
a.chk-link{text-decoration:none;color:inherit}
a.chk-link .badge{cursor:pointer}
a.chk-link:hover .badge,a.chk-link:focus .badge{outline:2px solid var(--accent);outline-offset:1px}
#checks tr[id^="chk-"]{scroll-margin-top:24px}
#checks tr:target td{background:#fbf3da;transition:background .3s}
.ztctl>summary{cursor:pointer;font-weight:650;color:var(--navy);white-space:nowrap}
.ztctl>.inside{margin-top:6px}
.ztbar{display:flex;height:12px;min-width:160px;border-radius:6px;overflow:hidden;margin:0 0 6px;background:#eef2f6}
.ztbar .seg{display:block;height:100%}
.ztbar .seg.INEFFECTIVE{background:#d79a9a}.ztbar .seg.AT_RISK{background:#e3bb7e}.ztbar .seg.EFFECTIVE{background:#88c3a3}
.ztbar .seg.INFORMATIONAL{background:#9bbfe3}.ztbar .seg.UNASSESSED{background:#c1cad7}.ztbar .seg.other{background:#d9dfe8}
.ztmap>summary{cursor:pointer;font-size:1.05em;font-weight:700;margin:14px 0 8px}
@media print{.ztbar{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""
LINKS18_TEXT = {
    "en-US": {"controls": "controls", "axis": "Axis", "maxrisk": "Max risk"},
    "pt-BR": {"controls": "controles", "axis": "Eixo", "maxrisk": "Risco máx."},
}

_render_without_links18 = render


def render(document, locale):
    import re as _re
    html_text = _render_without_links18(document, locale)
    words = LINKS18_TEXT.get(locale, LINKS18_TEXT["en-US"])
    chk = r'<span class="badge (CHK-\d+)">\1</span>'

    def section_bounds(text, sid):
        start = text.find(f'<section class="section" id="{sid}">')
        if start < 0:
            raise ValueError(f"report section {sid} not found")
        return start, text.index("</section>", start)

    # 1) Zero Trust x Tier summary: controls collapsed behind a count, outcome bar above the outcome badges.
    s, e = section_bounds(html_text, "zt")
    zt = html_text[s:e]
    first_table_end = zt.index("</table>")
    summary, rest = zt[:first_table_end], zt[first_table_end:]

    def controls_cell(m):
        pills = _re.findall(chk, m.group(1))
        if not pills:
            return m.group(0)
        return (f'<td><details class="ztctl"><summary>{len(pills)} {words["controls"]}</summary>'
                f'<div class="inside"><span class="pillset">{m.group(1)}</span></div></details></td>')

    summary = _re.sub(r'<td><span class="pillset">((?:<span class="badge CHK-\d+">CHK-\d+</span>)+)</span></td>', controls_cell, summary)

    def outcome_cell(m):
        parts = _re.findall(r'<span class="badge ([A-Z_]+):(\d+)">', m.group(1))
        if not parts:
            return m.group(0)
        known = {"INEFFECTIVE", "AT_RISK", "EFFECTIVE", "INFORMATIONAL", "UNASSESSED"}
        segs = "".join(f'<i class="seg {name if name in known else "other"}" style="flex:{count}" title="{name}: {count}"></i>' for name, count in parts)
        return f'<td><div class="ztbar" role="img" aria-label="{" · ".join(f"{n}: {c}" for n, c in parts)}">{segs}</div>{m.group(1)}</td>'

    summary = _re.sub(r'<td>(<span class="pillset">(?:<span class="badge [A-Z_]+:\d+">[A-Z_]+:\d+</span>)+</span>)</td>', outcome_cell, summary)
    summary = summary.replace("<th>Axis</th>", f'<th>{words["axis"]}</th>', 1).replace("<th>Max risk</th>", f'<th>{words["maxrisk"]}</th>', 1)
    # 64-check mapping table collapsed under its own heading
    rest = _re.sub(r'<h3>([^<]*)</h3>(<div class="tablewrap">.*?</table></div>)',
                   lambda m: f'<details class="ztmap"><summary>{m.group(1)}</summary><div class="inside">{m.group(2)}</div></details>',
                   rest, count=1, flags=_re.S)
    html_text = html_text[:s] + summary + rest + html_text[e:]

    # 2) Checks table rows get stable anchors.
    s, e = section_bounds(html_text, "checks")
    checks = _re.sub(r'<tr><td>(CHK-\d+)</td>', r'<tr id="chk-\1"><td>\1</td>', html_text[s:e])
    html_text = html_text[:s] + checks + html_text[e:]
    targets = set(_re.findall(r'<tr id="chk-(CHK-\d+)">', checks))
    if not targets:
        raise ValueError("Checks table rows not found for CHK anchors")

    # 3) Every CHK pill becomes a link to its Checks row (only when the row exists).
    html_text = _re.sub(chk, lambda m: (f'<a class="chk-link" href="#chk-{m.group(1)}">{m.group(0)}</a>' if m.group(1) in targets else m.group(0)), html_text)
    return html_text.replace("</style>", LINKS18_CSS + "</style>", 1)

# --- PR19-PRINT: print/PDF pagination (print-only CSS, render-only) ---
PRINT19_CSS = r"""
@media print{
.section,.narrative,details,.tablewrap{break-inside:auto!important}
.section{margin:0 0 6mm}
#overview,#zt,#scenarios,#defense,#risks,#cards,#roadmap,#checks,#evidence,#comparison{break-before:page}
h2,h3,h4,summary{break-after:avoid}
tr,.card,.plan-item,.plan-howto,li{break-inside:avoid}
thead{display:table-header-group}
.ztctl>.inside{display:none!important}.ztctl>summary{list-style:none}
}
"""

_render_without_print19 = render


def render(document, locale):
    html_text = _render_without_print19(document, locale)
    if "</style>" not in html_text:
        raise ValueError("report style block not found for print CSS")
    return html_text.replace("</style>", PRINT19_CSS + "</style>", 1)


# --- Report-style executive summary and posture vocabulary (render-only) -----
# Stored enums are unchanged. Only display wording changes: a control that is not
# verified or that offers a hardening opportunity is not presented as an insecure practice.
STATUS_LABELS["en-US"].update({
    "INEFFECTIVE": "Verified gap", "AT_RISK": "Improvement opportunity", "UNASSESSED": "Not verified",
    "EFFECTIVE": "Meets the criterion", "NOT_APPLICABLE": "Not applicable",
})
STATUS_LABELS["pt-BR"].update({
    "INEFFECTIVE": "Lacuna verificada", "AT_RISK": "Oportunidade de melhoria", "UNASSESSED": "Não verificado",
    "EFFECTIVE": "Atende ao critério", "NOT_APPLICABLE": "Não aplicável",
})
BASIS_LABELS = {
    "en-US": {"VERIFIED_GAP": "Remediate verified gaps", "IMPROVEMENT": "Improve posture", "EVIDENCE_COLLECTION": "Complete evidence collection"},
    "pt-BR": {"VERIFIED_GAP": "Corrigir lacunas verificadas", "IMPROVEMENT": "Melhorar a postura", "EVIDENCE_COLLECTION": "Completar a coleta de evidências"},
}
TEXT["en-US"].update({
    "narrativeTitle": "Executive summary",
    "sumVerdict": "{run} · {n} controls assessed. {gap} verified gap(s), {imp} improvement opportunity(ies) and {nv} control(s) not verified.",
    "sumHow": "A verified gap is a condition observed with enough evidence. An improvement opportunity is a hardening or visibility step that is not configured; it does not mean a practice is insecure. Not verified means the evidence was not collected or does not apply: it is a collection task, not a finding.",
    "sumGaps": "Verified gaps", "sumImprove": "Improvement opportunities", "sumNotVerified": "Not verified (evidence to complete)",
    "sumNone": "None.", "sumMore": "and {n} more in Checks.",
    "sumCheck": "Check", "sumObserved": "What was observed", "sumPriority": "Priority",
    "sumCodes": "Canonical codes", "sumLegend": "Legend: INEFFECTIVE = verified gap · AT_RISK = improvement opportunity · UNASSESSED = not verified.",
    "sumScope": "Reading guide",
    "sumRoadmap": "Planned actions (NOW)",
    "narrativeRun": "Run {run}",
    "planTitle": "Action plan - NOW",
    "planIntro": "Canonical roadmap order. Each action lists the checks that justify it, grouped by what to do: remediate verified gaps, improve posture, or complete evidence collection. Full detail is in Action Cards.",
    "planNoFailing": "No gap or improvement opportunity in this action; see Action Cards.",
})
TEXT["pt-BR"].update({
    "narrativeTitle": "Resumo executivo",
    "sumVerdict": "{run} · {n} controles avaliados. {gap} lacuna(s) verificada(s), {imp} oportunidade(s) de melhoria e {nv} controle(s) não verificado(s).",
    "sumHow": "Lacuna verificada é uma condição observada com evidência suficiente. Oportunidade de melhoria é um passo de hardening ou visibilidade que não está configurado; não significa que a prática seja insegura. Não verificado indica que a evidência não foi coletada ou não se aplica: é uma tarefa de coleta, não um achado.",
    "sumGaps": "Lacunas verificadas", "sumImprove": "Oportunidades de melhoria", "sumNotVerified": "Não verificado (evidências a completar)",
    "sumNone": "Nenhuma.", "sumMore": "e mais {n} em Checks.",
    "sumCheck": "Check", "sumObserved": "O que foi observado", "sumPriority": "Prioridade",
    "sumCodes": "Códigos canônicos", "sumLegend": "Legenda: INEFFECTIVE = lacuna verificada · AT_RISK = oportunidade de melhoria · UNASSESSED = não verificado.",
    "sumScope": "Como ler",
    "sumRoadmap": "Ações planejadas (NOW)",
    "narrativeRun": "Execução {run}",
    "planTitle": "Plano de ação - agora (NOW)",
    "planIntro": "Ordem do roadmap canônico. Cada ação lista os checks que a justificam, agrupados pelo que fazer: corrigir lacunas verificadas, melhorar a postura ou completar a coleta de evidências. O detalhe completo está em Action Cards.",
    "planNoFailing": "Nenhuma lacuna ou oportunidade de melhoria nesta ação; veja Action Cards.",
})
SUMMARY_CSS = r"""
.summary-verdict{font-size:15px;font-weight:650;margin:4px 0 6px}
.summary-how{margin:0 0 10px}
.sum-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin:8px 0}
.sum-card{border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:var(--panel)}
.sum-card strong{display:block;font-size:26px;line-height:1.1}
.sum-list h3{margin:14px 0 6px;font-size:15px}.sum-list .tablewrap table{min-width:0}
.basis-tag{display:inline-block;border-radius:6px;padding:0 6px;font-size:12px;font-weight:650;background:#eef2f7;color:#34465b;margin-left:6px}
.basis-VERIFIED_GAP{background:#f9ecec;color:#8a3737}.basis-IMPROVEMENT{background:#fbf1de;color:#7a5316}.basis-EVIDENCE_COLLECTION{background:#eef1f5;color:#4b586a}
.badge.NOT_APPLICABLE{background:#eef1f5;color:#4b586a}
"""
_CATALOG_TITLES: dict[str, dict[str, str]] | None = None
_STAT_ICONS = {
    "gap": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "imp": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "nv": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="11"/><line x1="11" y1="14" x2="11.01" y2="14"/></svg>',
}


def _outcome_bar(outcomes: dict[str, Any], labels: dict[str, str]) -> str:
    order = ("INEFFECTIVE", "AT_RISK", "UNASSESSED", "EFFECTIVE", "INFORMATIONAL", "NOT_APPLICABLE")
    total = sum(int(outcomes.get(key, 0)) for key in order) or 1
    segments = "".join(f'<i class="o-{key}" style="flex:{int(outcomes[key])}" title="{esc(labels.get(key, key))}: {int(outcomes[key])}"></i>'
                       for key in order if outcomes.get(key))
    legend = "".join(f'<span><i class="o-{key}"></i><b>{int(outcomes[key])}</b> {esc(labels.get(key, key))}</span>'
                     for key in order if outcomes.get(key))
    return f'<div class="ostack" role="img" aria-label="{total}">{segments}</div><div class="olegend">{legend}</div>'


def _check_titles(locale: str) -> dict[str, str]:
    global _CATALOG_TITLES
    if _CATALOG_TITLES is None:
        try:
            data = json.loads((ROOT / "criteria" / "v4" / "check-catalog.v4.json").read_text(encoding="utf-8-sig"))
            _CATALOG_TITLES = {row["id"]: row.get("title", {}) for row in data["checks"]}
        except (OSError, ValueError, KeyError):
            _CATALOG_TITLES = {}
    return {cid: (titles.get(locale) or titles.get("en-US") or cid) for cid, titles in _CATALOG_TITLES.items()}


def _short(text: Any, limit: int = 230) -> str:
    value = " ".join(str(text or "").split())
    if len(value) <= limit:
        return value
    cut = value[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "…"


def _summary_list(document: dict[str, Any], locale: str, outcome: str, heading: str, limit: int = 6) -> str:
    t = TEXT[locale]
    titles = _check_titles(locale)
    observations = {row["checkId"]: row for row in document["traceability"]["observations"]}
    rows = sorted((c for c in document["controlAssessments"] if c["outcome"] == outcome),
                  key=lambda c: (-c["residualRisk"]["score"], c["checkId"]))
    if not rows:
        return f'<div class="sum-list"><h3>{esc(heading)} (0)</h3><p class="muted">{esc(t["sumNone"])}</p></div>'
    body = table(
        [t["sumCheck"], t["sumObserved"], t["sumPriority"]],
        ([f'<strong>{esc(c["checkId"])}</strong><br>{esc(titles.get(c["checkId"], ""))}',
          esc(_short(observations.get(c["checkId"], {}).get("statement"))),
          badge(c["priority"])] for c in rows[:limit]),
    )
    more = f'<p class="muted">{esc(t["sumMore"].format(n=len(rows) - limit))}</p>' if len(rows) > limit else ""
    return f'<div class="sum-list"><h3>{esc(heading)} ({len(rows)})</h3>{body}{more}</div>'


def narrative_html(document: dict[str, Any], locale: str) -> str:
    t = TEXT[locale]
    labels = STATUS_LABELS[locale]
    meta = document["metadata"]
    assurance = document["assurance"]
    outcomes = assurance["controlOutcomes"]
    now = document["roadmap"]["NOW"]
    scenarios = document["securityScenarios"]
    comparison = document["comparison"]
    cards = {row["id"]: row for row in document["actionCards"]}
    confirmations = list(dict.fromkeys(row["attackConfirmation"] for row in scenarios))
    partial = assurance["evidenceCoverage"].get("PARTIAL")
    total = len(document["controlAssessments"])
    gap, imp, nv = (outcomes.get(key, 0) for key in ("INEFFECTIVE", "AT_RISK", "UNASSESSED"))
    verdict = t["sumVerdict"].format(run=meta["runId"], n=total, gap=gap, imp=imp, nv=nv)
    cards_html = (
        f'<div class="sum-grid">'
        f'<div class="sum-card gap"><span class="ico">{_STAT_ICONS["gap"]}</span><strong>{gap}</strong><span>{esc(labels["INEFFECTIVE"])}</span></div>'
        f'<div class="sum-card imp"><span class="ico">{_STAT_ICONS["imp"]}</span><strong>{imp}</strong><span>{esc(labels["AT_RISK"])}</span></div>'
        f'<div class="sum-card nv"><span class="ico">{_STAT_ICONS["nv"]}</span><strong>{nv}</strong><span>{esc(labels["UNASSESSED"])}</span></div></div>'
        + _outcome_bar(outcomes, labels)
    )
    roadmap = "".join(
        f'<li><b>{esc(row["actionCardId"])}</b> · {esc(cards.get(row["actionCardId"], {}).get("title"))}'
        f'<span class="basis-tag basis-{esc(cards.get(row["actionCardId"], {}).get("basis"))}">'
        f'{esc(BASIS_LABELS[locale].get(cards.get(row["actionCardId"], {}).get("basis"), ""))}</span></li>'
        for row in now
    )
    parts = [
        f'<p class="summary-verdict">{esc(verdict)}</p>',
        f'<p class="summary-how muted">{esc(t["sumHow"])}</p>',
        cards_html,
        _summary_list(document, locale, "INEFFECTIVE", t["sumGaps"]),
        _summary_list(document, locale, "AT_RISK", t["sumImprove"]),
        _summary_list(document, locale, "UNASSESSED", t["sumNotVerified"], limit=4),
        (f'<h3>{esc(t["sumRoadmap"])}</h3><ul class="now-list">{roadmap}</ul>' if now else f'<p class="muted">{esc(t["planEmpty"])}</p>'),
        f'<p class="muted"><b>{esc(t["sumCodes"])}:</b> {badges(f"{k}:{v}" for k, v in outcomes.items())} '
        f'{badges(f"{k}:{v}" for k, v in assurance["evidenceCoverage"].items())}<br>{esc(t["sumLegend"])}</p>',
        (f'<p><span class="narrative-partial">{esc(t["narrativePartial"].format(k=partial))}</span></p>' if partial else ""),
        f'<p>{esc(t["narrativeScenarios"].format(n=len(scenarios)))} {badges(confirmations)} {esc(t["narrativeNoAttack"])}</p>',
        (f'<p>{esc(t["narrativeNoBaseline"])}</p>' if comparison is None else
         f'<p>{esc(t["narrativeComparison"].format(run=comparison["baselineRunId"]))} '
         f'{badges(f"{k}:{v}" for k, v in comparison["summary"].items())}</p>'),
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
    observations = {row["checkId"]: row for row in document["traceability"]["observations"]}
    claims = {row["checkId"]: row for row in document["traceability"]["claims"]}
    evidence = {row["checkId"]: row for row in document["traceability"]["evidence"]}
    titles = _check_titles(locale)
    package = document["metadata"]["source"]["name"]
    playbooks = [(tuple(cards.get(row["actionCardId"], {}).get("actions", [])),
                  tuple(cards.get(row["actionCardId"], {}).get("closureEvidence", []))) for row in now]
    shared = bool(playbooks) and len(set(playbooks)) == 1

    def howto(actions: Iterable[Any], closure: Iterable[Any]) -> str:
        return (f'<div class="plan-howto"><h3>{esc(t["planHowTo"])}</h3>{ul(actions)}'
                f'<h3>{esc(t["planClosure"])}</h3>{ul(closure)}</div>')

    items = []
    for row in now:
        card = cards.get(row["actionCardId"], {})
        basis = card.get("basis", "VERIFIED_GAP")
        shown = ("INEFFECTIVE", "AT_RISK", "UNASSESSED") if basis == "EVIDENCE_COLLECTION" else ("INEFFECTIVE", "AT_RISK")
        listed = [cid for cid in row["controlIds"] if outcomes.get(cid) in shown]
        others = [cid for cid in row["controlIds"] if outcomes.get(cid) not in shown]
        checks = "".join(
            f'<li><span class="kpi k-{esc(outcomes[cid])}" title="{esc(outcomes[cid])}">{esc(labels.get(outcomes[cid], outcomes[cid]))}</span> '
            f'<b>{esc(cid)}</b> {esc(titles.get(cid, ""))} - {esc(observations.get(cid, {}).get("statement"))}'
            + evidence_trace_html(cid, evidence.get(cid, {}), observations.get(cid, {}), claims.get(cid, {}), package, locale)
            + "</li>"
            for cid in listed
        ) or f'<li class="muted">{esc(t["planNoFailing"])}</li>'
        other_html = (f'<div class="plan-others muted">{esc(t["planOthers"])} {esc(", ".join(others))}</div>' if others else "")
        items.append(
            f'<li class="plan-item" data-plan-card="{esc(row["actionCardId"])}">'
            f'<div class="plan-head"><span class="prio p-{esc(row["priority"])}">{esc(row["priority"])}</span> '
            f'<strong>{esc(row["actionCardId"])} · {esc(card.get("title"))}</strong>'
            f'<span class="basis-tag basis-{esc(basis)}">{esc(BASIS_LABELS[locale].get(basis, basis))}</span></div>'
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


_render_without_summary_css = render


def render(document, locale):
    html_text = _render_without_summary_css(document, locale)
    if "</style>" not in html_text:
        raise ValueError("report has no style block")
    return html_text.replace("</style>", SUMMARY_CSS + "</style>", 1)


# --- Navigation and visual theme (render-only post-processing) ---------------
TEXT["en-US"].update({
    "uxNavLabel": "Report sections", "uxMenu": "Menu", "uxTop": "Back to top",
    "uxGrpSummary": "Summary", "uxGrpAnalysis": "Posture analysis", "uxGrpExecution": "Execution", "uxGrpEvidence": "Evidence",
    "uxOverview": "Overview", "uxZt": "Zero Trust × Tier", "uxScenarios": "Scenarios", "uxDefense": "Defense coverage",
    "uxRisks": "Risks", "uxCards": "Action cards", "uxRoadmap": "Roadmap", "uxAssets": "Assets",
    "uxChecks": "Checks", "uxEvidence": "Evidence", "uxComparison": "Comparison",
    "uxFilter": "Filter checks by ID, title or text", "uxAll": "All", "uxShowing": "Showing",
    "uxPackage": "Package", "uxCollector": "Collector", "uxGenerated": "Generated", "uxIntegrity": "Integrity", "uxRun": "Run",
})
TEXT["pt-BR"].update({
    "uxNavLabel": "Seções do relatório", "uxMenu": "Menu", "uxTop": "Voltar ao topo",
    "uxGrpSummary": "Resumo", "uxGrpAnalysis": "Análise de postura", "uxGrpExecution": "Execução", "uxGrpEvidence": "Evidências",
    "uxOverview": "Visão geral", "uxZt": "Zero Trust × Tier", "uxScenarios": "Cenários", "uxDefense": "Cobertura de defesa",
    "uxRisks": "Riscos", "uxCards": "Action cards", "uxRoadmap": "Roadmap", "uxAssets": "Assets",
    "uxChecks": "Checks", "uxEvidence": "Evidências", "uxComparison": "Comparação",
    "uxFilter": "Filtrar checks por ID, título ou texto", "uxAll": "Todos", "uxShowing": "Exibindo",
    "uxPackage": "Pacote", "uxCollector": "Coletor", "uxGenerated": "Gerado em", "uxIntegrity": "Integridade", "uxRun": "Execução",
})
_ICONS = {
    "executive-narrative": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    "action-plan": '<polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "overview": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
    "zt": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "scenarios": '<line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>',
    "defense": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "risks": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "cards": '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    "roadmap": '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>',
    "assets": '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    "checks": '<polyline points="20 6 9 17 4 12"/>',
    "evidence": '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "comparison": '<circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7"/><line x1="6" y1="9" x2="6" y2="21"/>',
}


def _icon(key: str) -> str:
    return ('<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_ICONS[key]}</svg>')


def _ux_nav(document: dict[str, Any], locale: str, page: str) -> str:
    t = TEXT[locale]
    cards = len(document["actionCards"])
    groups = [
        ("uxGrpSummary", [("executive-narrative", t["narrativeTitle"], ""), ("action-plan", t["planTitle"].split(" - ")[0], str(len(document["roadmap"]["NOW"])))]),
        ("uxGrpAnalysis", [("overview", t["uxOverview"], ""), ("zt", t["uxZt"], ""), ("scenarios", t["uxScenarios"], str(len(document["securityScenarios"]))),
                           ("defense", t["uxDefense"], ""), ("risks", t["uxRisks"], "")]),
        ("uxGrpExecution", [("cards", t["uxCards"], str(cards)), ("roadmap", t["uxRoadmap"], "")]),
        ("uxGrpEvidence", [("checks", t["uxChecks"], str(len(document["controlAssessments"]))), ("evidence", t["uxEvidence"], ""),
                           ("assets", t["uxAssets"], ""), ("comparison", t["uxComparison"], "")]),
    ]
    out = []
    for group_key, items in groups:
        links = "".join(
            f'<a href="#{sid}"><span class="ni">{_icon(sid)}</span><span class="nl">{esc(label)}</span>'
            + (f'<span class="nc">{esc(count)}</span>' if count else "") + "</a>"
            for sid, label, count in items if f'id="{sid}"' in page
        )
        if links:
            out.append(f'<div class="ng">{esc(t[group_key])}</div>{links}')
    return f'<nav aria-label="{esc(t["uxNavLabel"])}">{"".join(out)}</nav>'


def _ux_hero_meta(document: dict[str, Any], locale: str) -> str:
    t = TEXT[locale]
    meta = document["metadata"]
    source = meta["source"]
    generated = str(meta["generatedAt"])[:16].replace("T", " ") + " UTC"
    chips = [
        (t["uxPackage"], source.get("name")), (t["uxCollector"], source.get("collectorVersion")),
        (t["uxGenerated"], generated), (t["uxIntegrity"], source.get("integrity")), (t["uxRun"], meta["runId"]),
    ]
    return '<div class="meta">' + "".join(f'<span><i>{esc(k)}</i> {esc(v)}</span>' for k, v in chips if v) + "</div>"


def _ux_checks(page: str, document: dict[str, Any], locale: str) -> str:
    import re as _re
    t = TEXT[locale]
    labels = STATUS_LABELS[locale]
    titles = _check_titles(locale)
    outcomes = ("INEFFECTIVE", "AT_RISK", "UNASSESSED", "EFFECTIVE", "INFORMATIONAL", "NOT_APPLICABLE")
    total = len(document["controlAssessments"])

    def row(match: Any) -> str:
        cid, inner = match.group(1), match.group(2)
        found = next((o for o in outcomes if f'<span class="badge {o}">' in inner), "")
        inner = inner.replace(f"<td>{cid}</td>", f'<td><b>{cid}</b><br><span class="ctitle">{esc(titles.get(cid, ""))}</span></td>', 1)
        if found:
            inner = inner.replace(f'<span class="badge {found}">{found}</span>',
                                  f'<span class="badge {found}" title="{found}">{esc(labels.get(found, found))}</span>', 1)
        return f'<tr id="chk-{cid}" data-o="{found}">{inner}</tr>'

    page = _re.sub(r'<tr id="chk-(CHK-\d+)">(.*?)</tr>', row, page, flags=_re.S)
    chips = "".join(
        f'<button type="button" class="chip{" on" if key == "ALL" else ""}" data-filter="{key}">{esc(text)}</button>'
        for key, text in (("ALL", t["uxAll"]), ("INEFFECTIVE", labels["INEFFECTIVE"]), ("AT_RISK", labels["AT_RISK"]),
                          ("UNASSESSED", labels["UNASSESSED"]), ("EFFECTIVE", labels["EFFECTIVE"]))
    )
    bar = (f'<div class="fbar"><input id="chkfilter" type="search" placeholder="{esc(t["uxFilter"])}" aria-label="{esc(t["uxFilter"])}">'
           f'<div class="chips">{chips}</div><span class="muted">{esc(t["uxShowing"])} <b id="chkcount">{total}</b> / {total}</span></div>')
    marker = f'<h2>{esc(t["checks"])}</h2>'
    if page.count(marker) != 1:
        raise ValueError("checks heading anchor not found for the filter bar")
    return page.replace(marker, marker + bar, 1)


UX_CSS = r"""
body{font:14px/1.6 "Segoe UI Variable Text","Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased}
.shell{grid-template-columns:272px minmax(0,1fr)}
.side{background:#fff;color:var(--ink);border-right:1px solid var(--line);padding:20px 14px;display:flex;flex-direction:column;gap:4px;box-shadow:none}
.brand{display:flex;align-items:center;gap:11px;font-size:15px;font-weight:650;color:var(--navy);padding:2px 6px 16px}
.brand .logo{display:grid;place-items:center;width:36px;height:36px;border-radius:10px;background:var(--navy);color:#fff;font-weight:700;font-size:13px;letter-spacing:.02em}
.brand small{color:var(--muted);font-size:11.5px;font-weight:450;margin-top:1px}
.side nav{display:flex;flex-direction:column;gap:1px;margin:0;flex:1}
.ng{margin:16px 8px 5px;font-size:10.5px;font-weight:650;letter-spacing:.09em;text-transform:uppercase;color:#8a96a8}
.side nav a{display:flex;align-items:center;gap:10px;padding:7px 10px;border-radius:8px;color:#3b4859;font-weight:500;white-space:normal;position:relative}
.side nav a .ni{display:grid;place-items:center;color:#8a96a8;flex:none}
.side nav a .nl{flex:1;min-width:0}
.side nav a .nc{flex:none;min-width:22px;text-align:center;font-size:11px;font-weight:600;color:#5d6a7e;background:#f1f4f8;border-radius:999px;padding:1px 7px}
.side nav a:hover{background:var(--panel);color:var(--ink)}
.side nav a.active{background:var(--soft);color:var(--navy);font-weight:600}
.side nav a.active .ni{color:var(--accent)}
.side nav a.active::before{content:"";position:absolute;left:-14px;top:8px;bottom:8px;width:3px;border-radius:0 3px 3px 0;background:var(--accent)}
.side nav a.active .nc{background:#fff;color:var(--navy)}
.side .toolbar{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0 0;padding-top:12px;border-top:1px solid var(--line)}
.side .toolbar .btn{padding:8px 10px;font-size:12.5px;border-radius:8px;background:#fff;color:#3b4859;border:1px solid var(--line-2);text-align:center}
.side .toolbar .btn:hover{background:var(--panel)}
.side .toolbar #print{grid-column:1/3;background:var(--navy);border-color:var(--navy);color:#fff}
.side .toolbar #print:hover{background:#2a4068}
.main{max-width:1180px;width:100%;margin:0 auto;padding:28px 36px 64px;counter-reset:sec}
.hero{background:var(--navy);border-radius:14px;border-bottom:3px solid #2f8fb0;padding:30px 34px 26px;box-shadow:none}
.hero h1{font-size:30px;font-weight:300;letter-spacing:-.01em;margin:0 0 4px}
.hero p{color:#b8c6dc;font-size:14.5px}
.hero .meta{gap:6px 24px;margin-top:20px}
.hero .meta span{background:none;border:0;border-radius:0;padding:0;color:#e3ebf7;font-weight:500;font-size:12.5px}
.hero .meta i{font-style:normal;font-weight:500;color:#8ea2c0;margin-right:7px;text-transform:uppercase;letter-spacing:.06em;font-size:10.5px}
#validation-notice{font-size:12.5px;line-height:1.5;padding:0 14px;margin:0 0 16px;background:#fbf7ec;border:solid #fbf7ec;border-width:10px 0;box-shadow:inset 3px 0 0 #d9b35f,0 0 0 1px #f0e3c4;color:#5e4a1f;border-radius:8px}
.section,#executive-narrative,#action-plan{scroll-margin-top:76px}
.section,.plan,.narrative{background:var(--paper);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);padding:28px 32px;margin:20px 0}
.narrative.notice{background:var(--paper);border-left:1px solid var(--line)}
.section h2,.narrative h2,.plan h2{display:flex;align-items:baseline;gap:14px;font-size:22px;font-weight:650;color:var(--navy);letter-spacing:-.01em;margin:0 0 8px;padding-bottom:14px;border-bottom:1px solid var(--line)}
.section h2::before,.narrative h2::before,.plan h2::before{counter-increment:sec;content:counter(sec,decimal-leading-zero);font-weight:300;font-size:26px;line-height:1;color:var(--accent)}
.sec-sub{margin:0 0 18px;color:var(--muted);font-size:14px}
.section h3,.narrative h3,.plan h3{color:var(--accent);font-size:15px;font-weight:650;margin:24px 0 8px}
.section .card h3,.section .card h4{margin:0 0 8px}
.plan-howto h3{margin:14px 0 6px}.plan-howto h3:first-child{margin-top:0}
.tablewrap{border:1px solid var(--line);border-radius:10px;background:#fff}
table{font-size:13px}
th{background:var(--navy);color:#fff;font-size:12px;font-weight:600;border-bottom:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
td,th{padding:10px 12px}
td{border-bottom:1px solid #edf1f6}
tbody tr:nth-child(even) td{background:#f7f9fc}
tbody tr:hover td{background:#eef3fa}
td .badge{white-space:nowrap}
.card{border:1px solid var(--line);border-radius:12px;background:var(--panel);box-shadow:none}
.metric strong{font-size:30px;font-weight:300;color:var(--navy)}
.ctitle{color:var(--muted);font-size:12px}
.notice{background:#eef3fa;border-left:3px solid var(--accent);border-radius:8px;color:var(--ink)}
.node{background:#eef3fa;border:1px solid #d3deee;color:var(--navy);font-weight:650}
.scenario{border:1px solid var(--line);border-radius:12px;box-shadow:none}
.scenario summary{background:var(--panel);color:var(--navy);padding:14px 18px}
.btn{border-radius:8px;border:1px solid var(--line-2)}
.fbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 12px}
.fbar input{flex:1 1 260px;min-width:0;padding:9px 12px;border:1px solid var(--line-2);border-radius:8px;font:inherit;background:#fff}
.fbar input:focus,.btn:focus-visible,.chip:focus-visible,.side nav a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line-2);background:#fff;border-radius:999px;padding:5px 12px;font:inherit;font-size:12.5px;font-weight:600;color:#3b4859;cursor:pointer}
.chip.on{background:var(--navy);border-color:var(--navy);color:#fff}
.sum-grid{gap:14px}
.sum-card{display:grid;grid-template-columns:auto 1fr;column-gap:14px;align-items:center;padding:16px 18px}
.sum-card .ico{grid-row:1/3;display:grid;place-items:center;width:40px;height:40px;border-radius:50%;background:#eef1f5;color:#4b586a}
.sum-card.gap .ico{background:#f9ecec;color:#8a3737}.sum-card.imp .ico{background:#fbf1de;color:#7a5316}.sum-card.nv .ico{background:#eef1f5;color:#4b586a}
.sum-card strong{font-size:34px;font-weight:300;line-height:1;color:var(--navy)}
.sum-card>span:last-child{color:var(--muted);font-size:13px}
.ostack{display:flex;gap:2px;height:8px;border-radius:999px;overflow:hidden;background:#eef1f5;margin:16px 0 8px}
.ostack i{display:block;min-width:3px}
.o-INEFFECTIVE{background:#d79a9a}.o-AT_RISK{background:#e3bb7e}.o-UNASSESSED{background:#c1cad7}.o-EFFECTIVE{background:#88c3a3}.o-INFORMATIONAL{background:#9bbfe3}.o-NOT_APPLICABLE{background:#e1e6ee}
.olegend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12px;color:var(--muted);margin-bottom:6px}
.olegend b{color:var(--ink)}.olegend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:baseline}
.plan-list{list-style:none;padding:0;margin:16px 0;display:grid;gap:14px;counter-reset:pl}
.plan-item{counter-increment:pl;margin:0;padding:16px 18px 14px;border:1px solid var(--line);border-radius:12px;background:#fff}
.plan-head{display:flex;align-items:center;flex-wrap:wrap;gap:8px 10px;font-size:15px;color:var(--navy)}
.plan-head::before{content:counter(pl);flex:none;display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--soft);color:var(--accent);font-weight:650;font-size:13px}
.plan-meta{margin:6px 0 0 36px}
.plan-checks{list-style:none;padding:0;margin:10px 0 0 36px}
.plan-checks li{margin:0;padding:9px 0;border-top:1px solid #edf1f6}
.plan-others{margin:6px 0 0 36px}
.plan-howto{background:var(--panel);border:1px solid var(--line);border-radius:10px}
.topbar,.veil{display:none}
.totop{position:fixed;right:22px;bottom:22px;z-index:20;width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:#fff;color:#3b4859;box-shadow:var(--shadow);cursor:pointer;opacity:0;pointer-events:none;transition:opacity .15s}
.totop.show{opacity:1;pointer-events:auto}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media(min-width:901px){#validation-notice{cursor:pointer;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden}#validation-notice.open{display:block;-webkit-line-clamp:unset}}
@media(max-width:900px){
.shell{display:block}
.topbar{display:flex;align-items:center;gap:10px;position:sticky;top:0;z-index:30;background:#ffffffee;backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:9px 12px}
.topbar button{border:1px solid var(--line-2);background:#fff;border-radius:8px;padding:6px 9px;display:grid;place-items:center;cursor:pointer}
.topbar .tt{font-weight:650;color:var(--navy)}.topbar .cur{margin-left:auto;color:var(--muted);font-size:12.5px;max-width:48%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.side{position:fixed;left:0;top:0;bottom:0;height:100vh;width:min(86vw,320px);z-index:40;transform:translateX(-104%);transition:transform .2s ease;box-shadow:0 0 40px #1f305033;overflow:auto}
body.navopen .side{transform:none}
body.navopen .veil{display:block;position:fixed;inset:0;background:#1f305066;z-index:35}
.side nav{display:flex;overflow:visible}
.side nav a.active::before{left:-14px}
.main{padding:14px 14px 50px}
.section,.plan,.narrative{padding:20px 18px;border-radius:12px}
.section h2,.narrative h2,.plan h2{font-size:19px;gap:10px}
.section h2::before,.narrative h2::before,.plan h2::before{font-size:22px}
.hero{padding:22px 20px 20px}.hero h1{font-size:24px}
.plan-meta,.plan-checks,.plan-others{margin-left:0}
.sum-card strong{font-size:28px}
#validation-notice{cursor:pointer;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3;overflow:hidden}
#validation-notice.open{display:block;-webkit-line-clamp:unset}
}
@media print{#validation-notice{display:block;-webkit-line-clamp:unset;overflow:visible}.topbar,.veil,.totop,.fbar{display:none!important}.main{max-width:none;padding:0}.section,.plan,.narrative{box-shadow:none;border-radius:0}tr[hidden]{display:table-row}.hero{border-radius:0}}
"""


SECTION_SUB = {
    "en-US": {
        "overview": "Run identity and the control outcome and evidence-coverage counts.",
        "zt": "How the controls map to the Zero Trust principles, pillars and tiers.",
        "scenarios": "Attack-path hypotheses made more or less relevant by the evidence. None is a confirmed attack.",
        "defense": "Which defense functions cover each scenario, and where coverage is missing.",
        "risks": "Risks with the checks and scenarios behind each one.",
        "cards": "What to do about each risk: owners, steps, closure evidence and rollback.",
        "roadmap": "Action cards in execution order (priority first, then residual score).",
        "assets": "Assets identified in the package.",
        "checks": "Every check with its outcome, tier, risk and priority. Filter by status or text.",
        "evidence": "For each check: the claim, the observation and the evidence behind it.",
        "comparison": "Change against the baseline package.",
    },
    "pt-BR": {
        "overview": "Identidade da execução e contagem dos resultados dos controles e da cobertura da evidência.",
        "zt": "Como os controles se distribuem entre princípios, pilares e tiers do Zero Trust.",
        "scenarios": "Hipóteses de caminho de ataque que a evidência torna mais ou menos relevantes. Nenhuma é um ataque confirmado.",
        "defense": "Quais funções de defesa cobrem cada cenário e onde falta cobertura.",
        "risks": "Riscos com os checks e os cenários por trás de cada um.",
        "cards": "O que fazer em cada risco: responsáveis, passos, evidência de encerramento e rollback.",
        "roadmap": "Action cards na ordem de execução (prioridade primeiro, depois score residual).",
        "assets": "Ativos identificados no pacote.",
        "checks": "Cada check com resultado, tier, risco e prioridade. Filtre por status ou texto.",
        "evidence": "Por check: a afirmação, a observação e a evidência que a sustenta.",
        "comparison": "Mudança em relação ao pacote de baseline.",
    },
}


def _ux_page(page: str, document: dict[str, Any], locale: str) -> str:
    import re as _re
    t = TEXT[locale]
    for sid, text in SECTION_SUB[locale].items():
        head = _re.search(r'<section class="section" id="' + sid + r'"><h2>[^<]*</h2>', page)
        if head:
            page = page[:head.end()] + f'<p class="sec-sub">{esc(text)}</p>' + page[head.end():]
    aside = _re.search(r'<aside class="side">.*?</aside>', page, _re.S)
    if not aside:
        raise ValueError("sidebar anchor not found for the navigation layer")
    side = (
        f'<aside class="side" id="sidebar"><div class="brand"><span class="logo">AP</span><span>Arc Posture Review<small>{esc(t["subtitle"])}</small></span></div>'
        f'{_ux_nav(document, locale, page)}'
        f'<div class="toolbar"><button class="btn" id="print">{esc(t["print"])}</button>'
        f'<button class="btn" id="expand">{esc(t["expand"])}</button><button class="btn" id="collapse">{esc(t["collapse"])}</button></div></aside>'
    )
    page = page[:aside.start()] + side + page[aside.end():]
    topbar = (f'<div class="topbar"><button type="button" id="navtoggle" aria-controls="sidebar" aria-label="{esc(t["uxMenu"])}">{_icon("overview")}</button>'
              f'<span class="tt">Arc Posture Review</span><span id="curlabel" class="cur"></span></div><div id="navveil" class="veil"></div>')
    shell = '<div class="shell">'
    if page.count(shell) != 1:
        raise ValueError("shell anchor not found for the navigation layer")
    page = page.replace(shell, shell + topbar, 1)
    hero = _re.search(r'(<header class="hero">.*?)<div class="meta">.*?</div>(</header>)', page, _re.S)
    if not hero:
        raise ValueError("hero anchor not found for the navigation layer")
    page = page[:hero.start()] + hero.group(1) + _ux_hero_meta(document, locale) + hero.group(2) + page[hero.end():]
    page = _ux_checks(page, document, locale)
    top = f'<button type="button" id="totop" class="totop" aria-label="{esc(t["uxTop"])}" title="{esc(t["uxTop"])}">↑</button>'
    anchor = '<script type="application/json" id="canonical-assessment">'
    if page.count(anchor) != 1:
        raise ValueError("script anchor not found for the back-to-top control")
    return page.replace(anchor, top + anchor, 1).replace("</style>", UX_CSS + "</style>", 1)


_render_without_ux = render


def render(document, locale):
    return _ux_page(_render_without_ux(document, locale), document, locale)


# ---------- pt-BR rendering of engine and collector text (display only; the embedded canonical JSON is untouched) ----------
_PT_PREFIX = [
    ("Remediate: ", "Corrigir: "), ("Improve posture: ", "Melhorar a postura: "), ("Complete evidence: ", "Completar evidências: "),
]
_PT_STATIC = [
    ("Confirm the verified gap in the listed checks and the machines or scope it affects.", "Confirme a lacuna verificada nas verificações listadas e as máquinas ou o escopo afetados."),
    ("Remediate the highest-severity listed checks first, through change control.", "Corrija primeiro as verificações listadas de maior severidade, por meio de controle de mudanças."),
    ("Re-run the collection and confirm the listed checks reach PASS.", "Execute a coleta novamente e confirme que as verificações listadas chegam a PASS."),
    ("Record the owner, the date and any accepted-risk decision.", "Registre o responsável, a data e qualquer decisão de risco aceito."),
    ("The evidence behind each listed check is complete (Evidence Coverage FULL).", "A evidência de cada verificação listada está completa (Evidence Coverage FULL)."),
    ("Review the listed checks and decide which hardening steps to adopt.", "Revise as verificações listadas e decida quais passos de hardening adotar."),
    ("Prioritize by the residual risk of each check and the criticality tier of the machines.", "Priorize pelo risco residual de cada verificação e pelo tier de criticidade das máquinas."),
    ("Apply approved changes through change control and record the owner and date.", "Aplique as mudanças aprovadas por controle de mudanças e registre o responsável e a data."),
    ("Each listed check is PASS, or an accepted-risk decision is recorded.", "Cada verificação listada está em PASS ou há uma decisão de risco aceito registrada."),
    ("Identify which evidence is missing, documentary or outside the collected scope for the listed checks.", "Identifique qual evidência está ausente, é documental ou está fora do escopo coletado nas verificações listadas."),
    ("Collect it: extend the collector scope, grant read access, or record the documentary evidence.", "Colete-a: amplie o escopo do coletor, conceda acesso de leitura ou registre a evidência documental."),
    ("Re-run the collection and re-evaluate; this is evidence work, not a confirmed exposure.", "Execute a coleta novamente e reavalie; é trabalho de evidência, não uma exposição confirmada."),
    ("Each listed check has FULL evidence or a documented N/A.", "Cada verificação listada tem evidência FULL ou um N/A documentado."),
    ("Owner and timestamp are recorded.", "Responsável e data/hora estão registrados."),
    ("If remediation affects connectivity or management, use the approved rollback for the environment and revalidate SB01-SB08 as applicable.", "Se a correção afetar a conectividade ou o gerenciamento, use o rollback aprovado do ambiente e revalide SB01-SB08 conforme aplicável."),
    ("A posture weakness is not evidence of exploitation or compromise.", "Uma fragilidade de postura não é evidência de exploração ou comprometimento."),
    # Risks (action card titles)
    ("Compromise of privileged identity", "Comprometimento de identidade privilegiada"),
    ("Unsafe onboarding identity or secret", "Identidade ou segredo de onboarding inseguro"),
    ("Control-plane privilege escalation", "Escalação de privilégio no plano de controle"),
    ("Network and name-resolution boundary bypass", "Contorno da fronteira de rede e de resolução de nomes"),
    ("Agent, extension, or local-control tampering", "Adulteração do agente, de extensões ou de controles locais"),
    ("Abuse of extensions and remote execution", "Abuso de extensões e de execução remota"),
    ("Security telemetry blind spot", "Ponto cego na telemetria de segurança"),
    ("Exploitation of vulnerability or legacy platform", "Exploração de vulnerabilidade ou de plataforma legada"),
    ("Governance, lifecycle, or scope drift", "Desvio de governança, ciclo de vida ou escopo"),
    ("SQL protection, entitlement, or telemetry failure", "Falha de proteção, licenciamento ou telemetria do SQL"),
    ("Operational resilience and recovery failure", "Falha de resiliência operacional e de recuperação"),
    # Scenarios
    ("Privileged identity takeover", "Tomada de identidade privilegiada"),
    ("Onboarding credential replay", "Reuso de credencial de onboarding"),
    ("Management-plane privilege escalation", "Escalação de privilégio no plano de gerenciamento"),
    ("Unintended management network path", "Caminho de rede de gerenciamento não previsto"),
    ("Arc agent trust degradation", "Degradação da confiança no agente Arc"),
    ("Extension or Run Command abuse", "Abuso de extensão ou de Run Command"),
    ("Telemetry suppression and delayed detection", "Supressão de telemetria e detecção tardia"),
    ("Exploit of vulnerable or legacy host", "Exploração de host vulnerável ou legado"),
    ("Governance and lifecycle drift", "Desvio de governança e de ciclo de vida"),
    ("SQL protection or usage-telemetry gap", "Lacuna de proteção do SQL ou de telemetria de uso"),
    ("Recovery and trusted-state failure", "Falha de recuperação e de estado confiável"),
    ("An attacker with stolen or weakly protected administrator credentials attempts to reach Arc management and hosts.", "Um atacante com credenciais de administrador roubadas ou fracamente protegidas tenta alcançar o gerenciamento do Arc e os hosts."),
    ("A leaked or overprivileged onboarding identity is replayed to enroll or alter managed resources.", "Uma identidade de onboarding vazada ou com privilégios excessivos é reutilizada para registrar ou alterar recursos gerenciados."),
    ("A principal exploits broad RBAC or an unreviewed control-plane operation to gain administrative execution.", "Um principal explora RBAC amplo ou uma operação do plano de controle não revisada para obter execução administrativa."),
    ("An attacker uses public access, open inbound management, or incorrect DNS to bypass the approved connectivity design.", "Um atacante usa acesso público, gerenciamento de entrada aberto ou DNS incorreto para contornar o desenho de conectividade aprovado."),
    ("An attacker or failure condition exploits an unsupported agent, failed extension, unsafe mode, or weak local control.", "Um atacante ou uma condição de falha explora um agente sem suporte, uma extensão com falha, um modo inseguro ou um controle local fraco."),
    ("A privileged actor deploys or invokes an unapproved extension or remote command for persistence or lateral movement.", "Um agente privilegiado implanta ou invoca uma extensão ou um comando remoto não aprovado para persistência ou movimentação lateral."),
    ("An attacker disables, evades, or benefits from missing Defender, MDE, Monitor, Sentinel, or Activity Log coverage.", "Um atacante desabilita, evita ou se beneficia da falta de cobertura de Defender, MDE, Monitor, Sentinel ou Activity Log."),
    ("An attacker exploits an unpatched, unsupported, weakly baselined, or unencrypted host.", "Um atacante explora um host sem patches, sem suporte, com baseline fraco ou sem criptografia."),
    ("Unmanaged scope, inconsistent policy, manual deployment, or unsafe decommission creates an exploitable gap.", "Escopo não gerenciado, policy inconsistente, implantação manual ou descomissionamento inseguro criam uma lacuna explorável."),
    ("An attacker or configuration failure affects SQL protection, privilege, telemetry, or entitlement evidence.", "Um atacante ou uma falha de configuração afeta a proteção, o privilégio, a telemetria ou a evidência de licenciamento do SQL."),
    ("An incident cannot be contained or recovered because rollback, health, removal, or exception evidence is missing.", "Um incidente não pode ser contido nem recuperado porque faltam evidências de rollback, integridade, remoção ou exceção."),
    # Security boundaries
    ("Identity and privileged-access boundary", "Fronteira de identidade e de acesso privilegiado"),
    ("Azure management-plane boundary", "Fronteira do plano de gerenciamento do Azure"),
    ("Connectivity and DNS boundary", "Fronteira de conectividade e DNS"),
    ("Host operating-system boundary", "Fronteira do sistema operacional do host"),
    ("Agent and extension boundary", "Fronteira de agente e extensões"),
    ("Detection and response boundary", "Fronteira de detecção e resposta"),
    ("SQL and protected-data boundary", "Fronteira do SQL e dos dados protegidos"),
    ("Delivery and lifecycle boundary", "Fronteira de entrega e ciclo de vida"),
    ("Render-only report: risk, priority, scenario and roadmap values are supplied by the Evaluation Engine.", "Relatório somente de renderização: os valores de risco, prioridade, cenário e roadmap vêm do Evaluation Engine."),
]
_PT_TOKENS = {
    "Verify explicitly": "Verificar explicitamente", "Use least privilege access": "Usar acesso com privilégio mínimo", "Assume breach": "Presumir violação",
    "Identity": "Identidade", "Endpoints": "Endpoints", "Apps": "Aplicativos", "Data": "Dados", "Infrastructure": "Infraestrutura", "Network": "Rede",
}
_PT_CACHE: dict[str, Any] | None = None


def _js_regex(source: str, flags: str) -> Any:
    import re as _re
    if source[:1].isalnum():
        # Rules are written for English collector text; never match inside a word of text that is already Portuguese ("controle(s)" contains "role(s)").
        source = r"(?<![A-Za-zÀ-ÿ0-9_])" + source
    return _re.compile(source, (_re.I if "i" in flags else 0) | (_re.S if "s" in flags else 0))


def _pt_data() -> dict[str, Any]:
    global _PT_CACHE
    if _PT_CACHE is not None:
        return _PT_CACHE
    import re as _re
    rules: list[Any] = []
    exact: dict[str, str] = {}
    catalog: list[tuple[str, str]] = []
    try:
        data = json.loads((ROOT / "criteria" / "v4" / "pt-br-detail-rules.json").read_text(encoding="utf-8-sig"))
        exact = dict(data.get("exact", {}))
        rules = [(_js_regex(p, f), "g" in f, r) for p, f, r in [*data.get("rules", []), *data.get("narrative", [])]]
    except (OSError, ValueError):
        pass
    try:
        pt_crit = {row["id"]: row.get("crit") for row in json.loads((ROOT / "criteria" / "checks.pt-BR.json").read_text(encoding="utf-8-sig"))}
        enriched = json.loads((ROOT / "assurance" / "v4" / "checkpoint3" / "data" / "checks.enriched.json").read_text(encoding="utf-8-sig"))
        for row in enriched["checks"] if isinstance(enriched, dict) else enriched:
            if row.get("resultCriteria") and pt_crit.get(row["id"]):
                catalog.append((row["resultCriteria"], pt_crit[row["id"]]))
    except (OSError, ValueError, KeyError):
        pass
    statics = sorted([*_PT_STATIC, *catalog], key=lambda pair: -len(pair[0]))
    _PT_CACHE = {"rules": rules, "exact": exact, "statics": statics, "re": _re}
    return _PT_CACHE


def _pt_text(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return text
    start = text.index(stripped)
    return text[:start] + _pt_core(stripped) + text[start + len(stripped):]


def _pt_core(text: str) -> str:
    data = _pt_data()
    stripped = text
    if stripped in _PT_TOKENS:
        return _PT_TOKENS[stripped]
    if stripped in data["exact"]:
        return data["exact"][stripped]
    out = text
    for prefix, replacement in _PT_PREFIX:
        out = out.replace(prefix, replacement)
    for english, portuguese in data["statics"]:
        if english in out:
            out = out.replace(english, portuguese)
    for rx, every, replacement in data["rules"]:
        expand = lambda m, r=replacement: data["re"].sub(r"\$(\d)", lambda g: m.group(int(g.group(1))) or "", r)
        out = rx.sub(expand, out, count=0 if every else 1)
    return out


def _localize_pt(page: str) -> str:
    import re as _re
    parts = _re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", page, flags=_re.S | _re.I)
    for index in range(0, len(parts), 2):
        raw = parts[index]
        if len(raw.strip()) < 3:
            continue
        source = html.unescape(raw)
        translated = _pt_text(source)
        if translated != source:
            # The canonical (engine/collector) text stays verbatim in the tooltip: the report contract requires canonical values to be present.
            tip = html.escape(source.strip(), quote=True)
            shown = html.escape(translated.strip(), quote=True)
            parts[index] = raw.replace(raw.strip(), f'<span class="i18n" title="{tip}">{shown}</span>', 1)
    return "".join(parts)


_render_before_localization = render


def render(document, locale):
    page = _render_before_localization(document, locale)
    return _localize_pt(page) if locale == "pt-BR" else page


if __name__ == "__main__":
    raise SystemExit(main())
