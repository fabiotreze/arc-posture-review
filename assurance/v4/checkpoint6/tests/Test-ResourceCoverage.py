#!/usr/bin/env python3
"""CP6 gate: resource index coverage (single-subscription inference, machines-column expansion, render guard)."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PORTAL = "https://portal.azure.com/#@/resource"


def _load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _package(folder: Path, subs: list[str]) -> tuple[Path, Path]:
    machines = [{"name": f"m{i + 1}", "id": f"/subscriptions/{sub}/resourceGroups/rg-a/providers/Microsoft.HybridCompute/machines/m{i + 1}"}
                for i, sub in enumerate(subs)]
    files = {
        "data/machines.json": json.dumps(machines),
        "findings/CHK-15.csv": "name,resourceGroup,purgeProtection,rbacAuthorization\nkv-one,rg-kv,False,True\n",
        "findings/CHK-33.csv": "assessment,machines,severity\nA,m1;m2,High\nB,3,Low\nC,m1,High\nD,ghost,Low\n",
        "findings/CHK-50.csv": "name,resourceGroup,setting\nthing,rg-x,off\n",
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name in sorted(files):
            archive.writestr(zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0)), files[name])
    zip_path = folder / f"pkg-{len(subs)}-{len(set(subs))}.zip"
    zip_path.write_bytes(buffer.getvalue())
    assessment = folder / "assessment.json"
    assessment.write_text(json.dumps({"metadata": {"runId": "ER-COVERAGE-TEST", "source": {"name": zip_path.name}}}), encoding="utf-8")
    return zip_path, assessment


def main() -> int:
    errors: list[str] = []
    tool = _load("new_resource_index", ROOT / "tools" / "New-ResourceIndex.py")
    sub = "00000000-0000-0000-0000-000000000001"
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        zip_path, assessment = _package(folder, [sub, sub])
        first = tool.build(zip_path, assessment)
        second = tool.build(zip_path, assessment)
        if json.dumps(first, sort_keys=False) != json.dumps(second, sort_keys=False):
            errors.append("index is not deterministic")
        if first.get("generator") != "New-ResourceIndex/1.1.0":
            errors.append(f"generator not bumped: {first.get('generator')}")
        kv = first["checks"]["CHK-15"][0]
        expected_kv = f"/subscriptions/{sub}/resourceGroups/rg-kv/providers/Microsoft.KeyVault/vaults/kv-one"
        if kv["kind"] != "inferred" or kv["resourceId"] != expected_kv or kv["portalUrl"] != PORTAL + expected_kv:
            errors.append(f"Key Vault inference wrong: {kv['kind']} {kv['resourceId']}")
        other = first["checks"]["CHK-50"][0]
        if other["kind"] != "resourceGroup-inferred" or other["resourceId"] != f"/subscriptions/{sub}/resourceGroups/rg-x":
            errors.append(f"resource group inference wrong: {other['kind']} {other['resourceId']}")
        rows = first["checks"]["CHK-33"]
        if [len(r["relatedResources"]) for r in rows] != [2, 0, 1, 1]:
            errors.append(f"machines expansion wrong: {[len(r['relatedResources']) for r in rows]}")
        if rows[0]["resourceId"] is not None or rows[0]["kind"] != "none":
            errors.append("multi-machine row must not get a primary link")
        if rows[2]["kind"] != "machines" or not str(rows[2]["portalUrl"]).startswith(PORTAL + "/subscriptions/"):
            errors.append("single-machine row must get a primary machine link")
        if rows[3]["resourceId"] is not None or rows[3]["relatedResources"][0]["portalUrl"] is not None:
            errors.append("unknown machine must stay unlinked")
        for check_rows in first["checks"].values():
            for row in check_rows:
                for item in [row] + row.get("relatedResources", []):
                    if item["resourceId"] and item["portalUrl"] != PORTAL + item["resourceId"]:
                        errors.append(f"URL rule broken: {item['portalUrl']}")
        zip_multi, assessment_multi = _package(folder, [sub, "00000000-0000-0000-0000-000000000002"])
        multi = tool.build(zip_multi, assessment_multi)
        if multi["checks"]["CHK-15"][0]["resourceId"] is not None or multi["checks"]["CHK-50"][0]["resourceId"] is not None:
            errors.append("inference must not happen with more than one subscription")

        render = _load("render_v4_coverage", ROOT / "assurance" / "v4" / "checkpoint6" / "report" / "render_v4.py")
        render._RESOURCE_INDEX = first
        block = render._related_block("CHK-33", True)
        if block.count('href="https://portal.azure.com/#@/resource/subscriptions/') != 2 or "Máquinas afetadas" not in block:
            errors.append("related machine links not rendered")
        if 'data-inferred-rows="1"' not in render._related_block("CHK-15", False):
            errors.append("inferred marker not rendered")
        render._resource_block_v10 = lambda *a, **k: '<div data-resource-index="unbound"></div>'
        if render._resource_block("CHK-33") != '<div data-resource-index="unbound"></div>':
            errors.append("unbound index must not render related links")
        render._resource_block_v10 = lambda *a, **k: "<div>Resources</div>"
        if "data-related-machines=\"2\"" not in render._resource_block("CHK-33"):
            errors.append("wrapper must append related links when bound")
        render._resource_block_v10 = lambda *a, **k: ""
        if render._resource_block("CHK-33") != "":
            errors.append("empty base block must stay empty")
    if errors:
        print(f"[FAIL] CP6 resource coverage: {len(errors)} error(s)")
        for error in errors:
            print(f" - {error}")
        return 1
    print("[PASS] CP6 resource coverage: inference, machines expansion, render guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
