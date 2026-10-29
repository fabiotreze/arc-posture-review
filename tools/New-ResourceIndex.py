#!/usr/bin/env python3
"""Build resource-index.v4.json (per-check Azure resource references) from a collection package.

Sidecar to assessment-result.v4: bound by runId and package SHA-256; read-only; deterministic.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

CONTRACT = "resource-index.v4"
GENERATOR = "New-ResourceIndex/1.0.0"
PORTAL = "https://portal.azure.com/#@/resource"
FINDING = re.compile(r"^findings/(CHK-\d+)\.csv$")
LABEL_KEYS = ("name", "machine", "displayName", "workspace", "roleName", "subscription", "assignment", "item", "capability", "category")
ARM_KEYS = ("resourceId", "id", "scope")


def _machines(package: zipfile.ZipFile) -> dict[tuple[str, str], str]:
    if "data/machines.json" not in package.namelist():
        return {}
    data = json.loads(package.read("data/machines.json").decode("utf-8-sig"))
    rows = data if isinstance(data, list) else data.get("value", data.get("data", []))
    index: dict[tuple[str, str], str] = {}
    for row in rows if isinstance(rows, list) else []:
        rid = str(row.get("id") or "")
        parts = rid.split("/")
        lowered = [p.lower() for p in parts]
        if "resourcegroups" in lowered and row.get("name"):
            rg = parts[lowered.index("resourcegroups") + 1]
            index[(str(row["name"]).lower(), rg.lower())] = rid
    return index


def _resolve(row: dict[str, str], machines: dict[tuple[str, str], str]) -> tuple[str | None, str]:
    for key in ARM_KEYS:
        value = (row.get(key) or "").strip()
        if value.lower().startswith("/subscriptions/"):
            return value, ("scope" if key == "scope" else "resource")
    for key, value in row.items():
        value = (value or "").strip()
        if value.lower().startswith("/subscriptions/"):
            return value, "resource"
    name = (row.get("name") or row.get("machine") or "").strip()
    rg = (row.get("resourceGroup") or "").strip()
    if name and rg and (name.lower(), rg.lower()) in machines:
        return machines[(name.lower(), rg.lower())], "machine"
    sub = (row.get("subscriptionId") or "").strip()
    if sub and rg:
        return f"/subscriptions/{sub}/resourceGroups/{rg}", "resourceGroup"
    if sub:
        return f"/subscriptions/{sub}", "subscription"
    return None, "none"


def build(evidence: Path, assessment: Path) -> dict:
    document = json.loads(assessment.read_text(encoding="utf-8-sig"))
    meta = document["metadata"]
    raw = evidence.read_bytes()
    package_sha = hashlib.sha256(raw).hexdigest()
    declared = str(meta.get("source", {}).get("packageDigest") or "")
    binding = "PACKAGE_DIGEST_MATCH" if declared.lower().removeprefix("sha256:") == package_sha else "RUN_ID_ONLY"
    checks: dict[str, list] = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as package:
        machines = _machines(package)
        for member in sorted(n for n in package.namelist() if FINDING.match(n)):
            check_id = FINDING.match(member).group(1)
            reader = csv.DictReader(io.StringIO(package.read(member).decode("utf-8-sig")))
            rows = []
            for row in reader:
                clean = {str(k): str(v if v is not None else "")[:200] for k, v in row.items() if k is not None}
                rid, kind = _resolve(clean, machines)
                label = next((clean[k] for k in LABEL_KEYS if clean.get(k)), None) or next((v for v in clean.values() if v), "-")
                rows.append({
                    "label": label,
                    "kind": kind,
                    "resourceId": rid,
                    "portalUrl": (PORTAL + rid) if rid else None,
                    "attributes": clean,
                })
            checks[check_id] = rows
    return {
        "contract": CONTRACT,
        "generator": GENERATOR,
        "runId": meta["runId"],
        "packageName": meta.get("source", {}).get("name"),
        "packageSha256": package_sha,
        "binding": binding,
        "checks": dict(sorted(checks.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build resource-index.v4.json from a collection package")
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--assessment", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    index = build(args.evidence, args.assessment)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8", newline="\n")
    linked = sum(1 for rows in index["checks"].values() for row in rows if row["resourceId"])
    total = sum(len(rows) for rows in index["checks"].values())
    print(f"[PASS] resource index {index['runId']} binding={index['binding']}: {len(index['checks'])} checks, {linked}/{total} rows with portal link -> {args.output}")
    return 0

# --- PR10-RESOURCE-COVERAGE (v1.1.0): single-subscription inference + machines-column expansion ---
GENERATOR = "New-ResourceIndex/1.1.0"
TYPE_BY_COLUMNS = (
    (frozenset({"purgeProtection", "rbacAuthorization"}), "Microsoft.KeyVault/vaults"),
)
_COVERAGE_STATE = {"subscription": None}


def _machine_ids(raw: bytes) -> dict[str, list[str]]:
    import io as _io
    import zipfile as _zipfile
    with _zipfile.ZipFile(_io.BytesIO(raw)) as package:
        if "data/machines.json" not in package.namelist():
            return {}
        data = json.loads(package.read("data/machines.json").decode("utf-8-sig"))
    rows = data if isinstance(data, list) else data.get("value", data.get("data", []))
    by_name: dict[str, list[str]] = {}
    for row in rows if isinstance(rows, list) else []:
        rid = str(row.get("id") or "") if isinstance(row, dict) else ""
        name = str(row.get("name") or "").lower() if isinstance(row, dict) else ""
        if name and rid.lower().startswith("/subscriptions/") and rid not in by_name.get(name, []):
            by_name.setdefault(name, []).append(rid)
    return {name: sorted(ids) for name, ids in sorted(by_name.items())}


def _single_subscription(by_name: dict[str, list[str]]) -> str | None:
    subs: dict[str, str] = {}
    for ids in by_name.values():
        for rid in ids:
            parts = rid.split("/")
            if len(parts) > 2 and parts[2]:
                subs.setdefault(parts[2].lower(), parts[2])
    return next(iter(subs.values())) if len(subs) == 1 else None


_resolve_v10 = _resolve


def _resolve(row, machines):
    rid, kind = _resolve_v10(row, machines)
    if rid:
        return rid, kind
    name = (row.get("name") or "").strip()
    rg = (row.get("resourceGroup") or "").strip()
    sub = _COVERAGE_STATE["subscription"]
    if not (name and rg and sub) or (row.get("subscriptionId") or "").strip():
        return rid, kind
    for columns, provider in TYPE_BY_COLUMNS:
        if columns <= set(row):
            return f"/subscriptions/{sub}/resourceGroups/{rg}/providers/{provider}/{name}", "inferred"
    return f"/subscriptions/{sub}/resourceGroups/{rg}", "resourceGroup-inferred"


def _related(attributes: dict, by_name: dict[str, list[str]]) -> list[dict]:
    value = str(attributes.get("machines") or "").strip().strip("[]")
    if not value or value.replace(".", "", 1).isdigit():
        return []
    names = []
    for part in re.split(r"[;|,]", value):
        part = part.strip().strip("'\"").strip()
        if part and part not in names:
            names.append(part)
    related = []
    for name in names[:50]:
        ids = by_name.get(name.lower(), [])
        rid = ids[0] if len(ids) == 1 else None
        related.append({"label": name, "resourceId": rid, "portalUrl": (PORTAL + rid) if rid else None})
    return related


_build_v10 = build


def build(evidence, assessment):
    by_name = _machine_ids(Path(evidence).read_bytes())
    _COVERAGE_STATE["subscription"] = _single_subscription(by_name)
    try:
        index = _build_v10(evidence, assessment)
    finally:
        _COVERAGE_STATE["subscription"] = None
    for rows in index["checks"].values():
        for row in rows:
            related = _related(row.get("attributes") or {}, by_name)
            row["relatedResources"] = related
            linked = [item for item in related if item["resourceId"]]
            if not row.get("resourceId") and len(related) == 1 and len(linked) == 1:
                row["resourceId"], row["portalUrl"], row["kind"] = linked[0]["resourceId"], linked[0]["portalUrl"], "machines"
    index["generator"] = GENERATOR
    return index


if __name__ == "__main__":
    raise SystemExit(main())
