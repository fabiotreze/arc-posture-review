#!/usr/bin/env python3
"""Gate the canonical 64-check catalog across source, renderer and collector $Eval blocks."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IDS = [f"CHK-{number:02d}" for number in range(1, 65)]
LOCALES = ("en-US", "pt-BR")
PENDING_EVAL_CONFIRMATION = ("CHK-12", "CHK-18", "CHK-19", "CHK-24", "CHK-28", "CHK-29", "CHK-31", "CHK-43")
DOMAIN_NAMES = {
    "A": "A · Architecture and scope",
    "B": "B · Governance and identity",
    "C": "C · Connectivity and network",
    "D": "D · Agent, extensions, and protection",
    "E": "E · Operations, monitoring, and auditing",
    "F": "F · Legacy",
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def json_var(text: str, name: str):
    marker = "var " + name + " = "
    start = text.find(marker)
    need(start >= 0, f"renderer variable missing: {name}")
    value, _end = json.JSONDecoder().raw_decode(text[start + len(marker):])
    return value


def collector_catalog(script: str) -> list[dict]:
    match = re.search(r"\$Catalog = @'\n(.*?)\n'@ \| ConvertFrom-Json", script, re.DOTALL)
    need(match is not None, "collector Catalog block missing")
    return json.loads(match.group(1))


def eval_blocks(script: str) -> dict[str, str]:
    starts = list(re.finditer(r"(?m)^\$Eval\['(CHK-\d{2})'\]\s*=\s*\{", script))
    blocks: dict[str, str] = {}
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else script.find("\n# With a machine limit", match.end())
        need(end > match.end(), f"cannot delimit collector Eval block: {match.group(1)}")
        blocks[match.group(1)] = script[match.start():end]
    return blocks


def load_sources() -> dict[str, list[dict]]:
    sources = {
        locale: json.loads((ROOT / f"criteria/checks.{locale}.json").read_text(encoding="utf-8"))
        for locale in LOCALES
    }
    required = {
        "id", "dom", "sev", "type", "ds", "title", "crit", "resultCriteria", "refs",
        "key", "layer", "mcsb", "tree", "hz", "owner", "steps", "how",
    }
    for locale, items in sources.items():
        ids = [item.get("id") for item in items]
        need(ids == EXPECTED_IDS, f"{locale}: expected ordered CHK-01..CHK-64, found {len(ids)} entries")
        need(len(ids) == len(set(ids)), f"{locale}: duplicate criterion ID")
        for item in items:
            missing = required - set(item)
            need(not missing, f"{locale} {item.get('id')}: missing source fields {sorted(missing)}")
            need(item["type"] in {"auto", "manual"}, f"{locale} {item['id']}: invalid type {item['type']}")
            need(bool(item["resultCriteria"].strip()), f"{locale} {item['id']}: empty final result criterion")
    structural = ("id", "dom", "type", "ds", "refs", "key", "layer", "mcsb", "tree", "hz")
    for en_item, pt_item in zip(sources["en-US"], sources["pt-BR"]):
        for field in structural:
            need(en_item[field] == pt_item[field], f"locale structure drift: {en_item['id']}.{field}")
    return sources


def check_renderer(sources: dict[str, list[dict]]) -> None:
    for locale in LOCALES:
        path = ROOT / f"arc-posture-review.{locale}.html"
        text = path.read_text(encoding="utf-8")
        need(json_var(text, "ITEMS") == sources[locale], f"{path.name}: ITEMS drift from criteria source")
        label = '"Criteria": x.it.resultCriteria || x.it.crit' if locale == "en-US" else '"Critério": x.it.resultCriteria || x.it.crit'
        need(label in text, f"{path.name}: final criterion is not emitted into the evidence matrix")
    need((ROOT / "index.html").read_bytes() == (ROOT / "arc-posture-review.en-US.html").read_bytes(), "index.html drift")


def check_collector(sources: dict[str, list[dict]]) -> None:
    script = (ROOT / "scripts/Invoke-ArcPostureReview.ps1").read_text(encoding="utf-8")
    en_items = sources["en-US"]
    checks_match = re.search(r"\[string\[\]\]\$Checks = @\((.*?)\),\n  \[string\]\$OutputRoot", script, re.DOTALL)
    need(checks_match is not None, "collector Checks parameter missing")
    checks = re.findall(r"'((?:CHK)-\d{2})'", checks_match.group(1))
    need(checks == EXPECTED_IDS, "collector default Checks must be the ordered canonical 64 IDs")

    catalog = collector_catalog(script)
    need([item["id"] for item in catalog] == EXPECTED_IDS, "collector Catalog IDs drift")
    by_id = {item["id"]: item for item in catalog}
    for item in en_items:
        expected = {
            "id": item["id"], "domain": DOMAIN_NAMES[item["dom"]], "title": item["title"],
            "sev": item["sev"], "type": item["type"], "ds": item["ds"], "refs": item["refs"],
        }
        need(by_id[item["id"]] == expected, f"collector Catalog drift: {item['id']}")

    blocks = eval_blocks(script)
    automatic = {item["id"] for item in en_items if item["type"] == "auto"}
    manual = {item["id"] for item in en_items if item["type"] == "manual"}
    need(set(blocks) == automatic, f"collector Eval coverage drift: missing={sorted(automatic-set(blocks))}, extra={sorted(set(blocks)-automatic)}")
    need(not (manual & set(blocks)), "manual checks must not have automatic Eval blocks")
    for check_id, block in blocks.items():
        need("Write-Result" in block, f"{check_id}: Eval block does not emit a result")

    markers = {
        "CHK-12": ["$DS['roles']", "identityPrincipalId", "principalId", "Write-Result 'FAIL'", "Write-Result 'WARN'", "Write-Result 'PASS'"],
        "CHK-18": ["$DS['related']", "microsoft.hybridcompute/privatelinkscopes", "publicNetworkAccess", "Disabled", "Write-Result 'N/A'", "Write-Result 'FAIL'", "Write-Result 'PASS'"],
        "CHK-19": ["$DS['related']", "privatelink.his.arc.azure.com", "privatelink.guestconfiguration.azure.com", "microsoft.network/dnsresolvers", "Write-Result 'N/A'", "Write-Result 'WARN'", "Write-Result 'PASS'"],
        "CHK-24": ["$DS['extensions']", "AdminCenter|OpenSSH|AADSSHLogin|AADLoginForWindows", "HybridWorker|CustomScript", "Write-Result 'WARN'", "Write-Result 'PASS'"],
        "CHK-28": ["$DS['extensions']", "$_.state -ne 'Succeeded'", "Write-Result 'FAIL'", "Write-Result 'PASS'"],
        "CHK-29": ["Get-AgentRelease", "$SupportCutoff", "$AgentSecFloor", "CVE-2026-26117", "Write-Result 'FAIL'", "Write-Result 'WARN'", "Write-Result 'PASS'"],
        "CHK-31": ["$DS['pricing']", "VirtualMachines", "Standard", "Write-Result 'FAIL'", "Write-Result 'PASS'"],
        "CHK-43": ["$DS['diag']", "workspaceId", "Write-Result 'FAIL'", "Write-Result 'PASS'"],
    }
    for check_id in PENDING_EVAL_CONFIRMATION:
        block = blocks.get(check_id, "")
        for marker in markers[check_id]:
            need(marker in block, f"{check_id}: missing Eval marker {marker}")
    need("privatelink.dp.kubernetesconfiguration.azure.com" not in blocks["CHK-19"], "CHK-19 Eval is server-scoped and must not claim the Arc-enabled Kubernetes DNS zone")

    # The recovered final matrix had one overclaim for CHK-19 (three zones plus end-to-end DNS
    # resolution). The canonical source is deliberately bounded to the two zones the collector
    # actually observes and to presence in the collected scope.
    chk19 = next(item for item in en_items if item["id"] == "CHK-19")["resultCriteria"]
    need("privatelink.his.arc.azure.com" in chk19 and "privatelink.guestconfiguration.azure.com" in chk19, "CHK-19 final criterion lost required server zones")
    need("privatelink.dp.kubernetesconfiguration.azure.com" not in chk19 and "linked/resolvable" not in chk19, "CHK-19 final criterion overclaims evidence not produced by $Eval")


def main() -> int:
    try:
        sources = load_sources()
        check_renderer(sources)
        check_collector(sources)
    except (AssertionError, KeyError, OSError, json.JSONDecodeError) as exc:
        print("FAIL criteria coverage:", exc)
        return 1
    print("PASS criteria coverage: 64 canonical checks synchronized; 45 automatic Eval blocks and 19 manual checks; CHK-12/18/19/24/28/29/31/43 confirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
