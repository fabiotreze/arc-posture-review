#!/usr/bin/env python3
"""Selective PT-BR narrative localization and EN-US/PT-BR parity gate."""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

FORBIDDEN_NARRATIVE = [
    "One vault has a definite baseline gap",
    "228 Defender recommendations affect Arc machines",
    "The report body is summarized",
    "Sentinel exists in the collected scope",
    "conclusive FAIL for the observed workspace",
    "Coverage is PARTIAL only because",
    "Canonical patch evidence: exactly one row",
    "authority or valid assessment is unknown",
    "affected machines: four NonCompliant",
    "Four SQL extensions have conclusive technical failures",
    "Evidence Coverage is PARTIAL",
    "Collector dataset(s); CLI calls and failures are recorded",
    "Defined by the check detail and findings rows",
    "Machine sampling when MaxMachines is set",
    "Point-in-time at collection; Activity Log uses ActivityDays",
    "Missing dataset = ERROR; proxy/external scope = PARTIAL",
    "Documentary control: validate with the customer",
    "What to do",
    "How to decide",
    "Evidence contract by check",
    "Executive assessment",
    "Evidence appendix",
]

REQUIRED_PT = [
    "Um Key Vault tem uma lacuna comprovada no baseline",
    "228 recomendações do Defender afetam máquinas Arc",
    "Há Microsoft Sentinel no escopo coletado",
    "FAIL conclusivo para o workspace observado",
    "A cobertura é PARTIAL somente porque pode existir um workspace de SOC externo fora do escopo",
    "Evidência canônica de patches: exatamente uma linha",
    "5 máquinas afetadas: quatro NonCompliant",
    "Quatro extensões SQL têm falhas técnicas conclusivas",
    "o entitlement de pCore permanece fora do pacote",
    "Cobertura da evidência é PARTIAL",
    "dataset(s) do coletor; comando e falhas em results.json/run.log",
    "subscription/linhas de evidência",
    "snapshot na hora da coleta",
    "fixture sanitizada de revisão do lab; 1 subscription; 7 máquinas Arc",
    "Avaliação executiva",
    "Apêndice de evidências",
    "Contrato de evidência por verificação",
    "O que fazer",
    "Como decidir",
]

PRESERVED_TOKENS = [
    "PASS", "WARN", "FAIL", "PARTIAL", "INFO", "TODO", "N/A",
    "CHK-41", "CHK-64", "findings/CHK-33.csv", "AutomaticByPlatform",
    "AzureMonitorWindowsAgent", "Microsoft.Azure.Monitor", "rg-lab-sanitized",
]


def meaningful_text(soup: BeautifulSoup) -> str:
    # Commands/code and raw evidence previews are explicitly outside localization scope.
    clone = BeautifulSoup(str(soup), "html.parser")
    for node in clone.select("pre, code, details.items table"):
        node.decompose()
    return " ".join(clone.get_text(" ", strip=True).split())


def status_signature(soup: BeautifulSoup) -> Counter[str]:
    signature: Counter[str] = Counter()
    for details in soup.select("details.pr[id^='pr-CHK-']"):
        check_id = details.get("id", "").replace("pr-", "")
        chip = details.select_one("summary .chip")
        if chip:
            status = chip.get_text(" ", strip=True).split()[0]
            signature[f"{check_id}:{status}"] += 1
    return signature


def raw_titles(soup: BeautifulSoup) -> list[str]:
    return sorted(set(re.findall(r"Sanitized recommendation \d+", soup.get_text(" ", strip=True))))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--en", type=Path, required=True)
    parser.add_argument("--pt", type=Path, required=True)
    args = parser.parse_args()
    try:
        en_raw = args.en.read_text(encoding="utf-8")
        pt_raw = args.pt.read_text(encoding="utf-8")
        en = BeautifulSoup(en_raw, "html.parser")
        pt = BeautifulSoup(pt_raw, "html.parser")
        pt_text = meaningful_text(pt)
        missing = [text for text in REQUIRED_PT if text not in pt_text]
        leaked = [text for text in FORBIDDEN_NARRATIVE if text in pt_text]
        if missing:
            raise AssertionError("missing localized narrative: " + " | ".join(missing))
        if leaked:
            raise AssertionError("English Arc Posture Review narrative leaked into PT-BR: " + " | ".join(leaked))
        if status_signature(en) != status_signature(pt):
            raise AssertionError("priority/status parity drift between EN-US and PT-BR")
        en_ids = sorted(set(re.findall(r"\b(?:CHK|CTL|REQ|DEC|ALR)-\d+\b", en_raw)))
        pt_ids = sorted(set(re.findall(r"\b(?:CHK|CTL|REQ|DEC|ALR)-\d+\b", pt_raw)))
        if en_ids != pt_ids:
            raise AssertionError("CHK/CTL/REQ/DEC/ALR identifier parity drift")
        if raw_titles(en) != raw_titles(pt) or not raw_titles(en):
            raise AssertionError("raw Defender recommendation titles were translated or lost")
        for token in PRESERVED_TOKENS:
            if token not in pt_raw:
                raise AssertionError(f"preserved raw token missing from PT-BR: {token}")
        # Raw evidence CSV/JSON and commands remain referenced, not translated or rewritten.
        if "data/machines.json" not in pt_raw or "findings/CHK-42.csv" not in pt_raw:
            raise AssertionError("raw dataset/evidence references missing")
        if 'arg("").resources' not in pt_raw or "azcmagent check" not in pt_raw:
            raise AssertionError("KQL/azcmagent content missing")
    except (AssertionError, OSError) as exc:
        print("FAIL localization parity:", exc)
        return 1
    print("PASS localization parity: PT-BR narrative localized; statuses, IDs, raw Azure/evidence values and Defender titles preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
