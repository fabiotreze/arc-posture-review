#!/usr/bin/env python3
"""Regression contract for v3.9.2 validation findings remediated in v3.9.5."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COUNTS = {"PASS": 8, "WARN": 8, "FAIL": 10, "INFO": 10, "N/A": 3, "TODO": 19, "PARTIAL": 6}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def eval_block(script: str, check_id: str) -> str:
    match = re.search(
        r"\$Eval\['" + re.escape(check_id) + r"'\] = \{(.*?)(?=\n\$Eval\['CHK-|\n# With a machine limit)",
        script,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"collector block missing: {check_id}")
    return match.group(1)


def check_fixture() -> None:
    expected = json.loads((ROOT / "tests/fixtures/reviewed-lab-expected.json").read_text(encoding="utf-8"))
    need(len(expected) == 64, f"review disposition must contain 64 checks, found {len(expected)}")
    counts = Counter(value["status"] for value in expected.values())
    need(dict(counts) == EXPECTED_COUNTS, f"review disposition counts drifted: {dict(counts)}")
    required = {
        "CHK-05": "PARTIAL", "CHK-23": "FAIL", "CHK-32": "PARTIAL", "CHK-33": "FAIL",
        "CHK-39": "FAIL", "CHK-40": "PARTIAL", "CHK-41": "FAIL", "CHK-42": "PARTIAL",
        "CHK-54": "PARTIAL", "CHK-55": "FAIL", "CHK-56": "FAIL", "CHK-57": "PARTIAL",
        "CHK-58": "FAIL", "CHK-64": "FAIL",
    }
    need(all(expected[c]["status"] == status for c, status in required.items()), "reviewed status transition drift")

    archive = ROOT / "tests/fixtures/reviewed-lab-sanitized.zip"
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        result_name = next(name for name in names if name.endswith("/results.json"))
        prefix = result_name[: -len("results.json")]
        result = json.loads(z.read(result_name))
        need(result["version"] == "v3.9.4" and result.get("schemaVersion") == 3 and len(result["results"]) == 64, "fixture result contract and backward compatibility")
        semantics = result.get("resultSemantics", {})
        need("independent" in semantics.get("evidenceCoverage", "").lower(), "fixture result/coverage semantics")
        manifest = json.loads(z.read(prefix + "manifest.json"))
        for item in manifest["files"]:
            payload = z.read(prefix + item["path"])
            need(len(payload) == item["size"], f"fixture size mismatch: {item['path']}")
            need(hashlib.sha256(payload).hexdigest().upper() == item["sha256"], f"fixture hash mismatch: {item['path']}")
        defender = z.read(prefix + "findings/CHK-33.csv").decode("utf-8")
        need(len(defender.splitlines()) - 1 == 228, "CHK-33 full-evidence boundary fixture must contain 228 rows")
        raw = b"\n".join(z.read(name) for name in names if not name.endswith("/"))
        for forbidden in [b"MCAPS-Hybrid", b"microsoft.com", b"SQLNODE", b"app01", b"DC1", b"FS1"]:
            need(forbidden not in raw, f"fixture is not sanitized: {forbidden.decode()}")


def check_collector() -> None:
    script = (ROOT / "scripts/Invoke-ArcPostureReview.ps1").read_text(encoding="utf-8")
    need("$ScriptVersion = 'v3.9.5'" in script, "collector version")
    need('"title":"MDE extension deployed through Arc"' in script, "CHK-32 title must describe the Arc extension proxy")
    need('"id":"CHK-33"' in script and '"title":"Defender recommendations","sev":"High"' in script, "CHK-33 severity")
    need("'ERRO'" not in script and "'PARCIAL'" not in script, "collector must emit canonical ERROR/PARTIAL statuses")

    checks = {
        "CHK-05": ["Write-Result 'PARTIAL'", "data-residency policy was not supplied"],
        "CHK-15": ["kvPurgePresent", "kvRbacPresent", "Missing/null is evidence unknown", "Write-Result 'PARTIAL'"],
        "CHK-23": ["Write-Result 'FAIL'", "Ceiling($m.Count / 2)"],
        "CHK-32": ["Write-Result 'PARTIAL'", "confirm sensor onboarding and health in the Defender portal"],
        "CHK-33": ["if ($hi -gt 0)", "Write-Result 'FAIL'", "body is intentionally summarized", "findings/CHK-33.csv"],
        "CHK-39": ["$rows.Count -eq $m.Count", "Write-Result 'FAIL'"],
        "CHK-40": ["Assessment blocked", "Write-Result 'PARTIAL'"],
        "CHK-41": ["Write-Result 'FAIL'", "conclusive failure for the observed workspace", "Evidence Coverage is PARTIAL"],
        "CHK-42": ["exactly one row per machine", "validAssessment", "external/not documented", "Write-Result 'PARTIAL'"],
        "CHK-45": ["resolve CHK-39 (AMA) and CHK-40 (DCR association)"],
        "CHK-54": ["Zero findings without confirmed coverage", "Write-Result 'PARTIAL'"],
        "CHK-55": ["($none.Count + $nc.Count)", "Write-Result 'FAIL'"],
        "CHK-56": ["$none.Count -eq $m.Count", "Write-Result 'FAIL'"],
        "CHK-57": ["MDE extension absence does not prove sensor absence", "Write-Result 'PARTIAL'"],
        "CHK-58": ["$blind.Count -eq $rows.Count", "Write-Result 'FAIL'"],
    }
    for check_id, markers in checks.items():
        body = eval_block(script, check_id)
        for marker in markers:
            need(marker in body, f"{check_id}: missing regression marker: {marker}")

    sql = eval_block(script, "CHK-64")
    need(sql.index("$age -gt 24") < sql.index("if ($m.status -ne 'Connected')"), "CHK-64 must count stale upload even when disconnected")
    need("no upload for more than 24 hours: {5}" in sql, "CHK-64 summary arithmetic")
    need("observed technical failure is conclusive" in sql and "Evidence Coverage is PARTIAL" in sql, "CHK-64 conclusive-result semantics")
    need("evidenceCoverage" in script and "evidenceSources" in script and "collectedAt" in script, "per-check evidence metadata")
    need("Control Result and Evidence Coverage are independent axes" in script, "global result/coverage semantics")
    need("'schemaVersion' { 3 }" in script, "collector schema v3")


def check_apps() -> None:
    for name in ["arc-posture-review.en-US.html", "arc-posture-review.pt-BR.html", "index.html"]:
        text = (ROOT / name).read_text(encoding="utf-8")
        need("Assessment Coverage" in text or "Cobertura da avaliação" in text, f"{name}: coverage metric")
        need("Evidence contract by check" in text or "Contrato de evidência por verificação" in text, f"{name}: evidence contract")
        need("Score before rounding" in text or "Nota antes do arredondamento" in text, f"{name}: score traceability")
        need("full-evidence" in text, f"{name}: complete CSV evidence link")
        need(not re.search(r"\.st-ERRO(?!R)|\.st-PARCIAL", text), f"{name}: legacy CSS taxonomy")
        need("btnGuideMd" not in text and 'id="mdSource"' not in text, f"{name}: retired Guide Markdown surface")
        need("Canonical project guide for v3.9.5" in text or "Guia canônico do projeto para a v3.9.5" in text, f"{name}: canonical HTML guide marker")
        need("Executive assessment" in text or "Avaliação executiva" in text, f"{name}: executive assessment boundary")
        need("Evidence appendix" in text or "Apêndice de evidências" in text, f"{name}: evidence appendix boundary")
        need("Control Result and Evidence Coverage are independent" in text or "Resultado do controle e Cobertura da evidência são eixos independentes" in text, f"{name}: result semantics")

    en = (ROOT / "arc-posture-review.en-US.html").read_text(encoding="utf-8")
    pt = (ROOT / "arc-posture-review.pt-BR.html").read_text(encoding="utf-8")
    need('"id":"CHK-23"' in en and "FAIL when at least half" in en, "CHK-23 Result x Criteria sync")
    need("High severity" in en and '"id":"CHK-33"' in en, "CHK-33 Result x Criteria sync")
    need("no connected machine has AMA" in en, "CHK-39 Result x Criteria sync")
    need("Sentinel exists in the collected scope" in en, "CHK-41 Result x Criteria sync")
    need("no connected Windows machine" in en, "CHK-56 Result x Criteria sync")
    need("every connected machine lacks both" in en, "CHK-58 Result x Criteria sync")
    for forbidden in ["Unknown confidence", "High confidence", "Medium confidence", "Low confidence", "Evidence appendix", "Executive assessment"]:
        need(forbidden not in pt, f"PT-BR renderer contains untranslated UI: {forbidden}")
    need('label: p == null ? "Desconhecida" : p >= 90 ? "Alta" : p >= 70 ? "Média" : "Baixa"' in pt, "PT-BR confidence localization")
    need((ROOT / "tools/Generate-CleanPdf.py").exists(), "clean PDF generator")


def main() -> int:
    try:
        check_fixture()
        check_collector()
        check_apps()
    except (AssertionError, KeyError, StopIteration, zipfile.BadZipFile) as exc:
        print("FAIL", exc)
        return 1
    print("PASS reviewed-lab corrections: 64-check disposition, collector rules, evidence coverage, arithmetic and sanitized E2E fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
