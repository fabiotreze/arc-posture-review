#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "v4"

EXPECTED = {
    "observation.schema.json",
    "evidence.schema.json",
    "claim.schema.json",
    "control.schema.json",
    "risk.schema.json",
    "action-card.schema.json",
    "validation.schema.json",
    "comparison.schema.json",
}

errors: list[str] = []

actual = {p.name for p in SCHEMA_DIR.glob("*.json")}

missing = EXPECTED - actual
unexpected = actual - EXPECTED

for name in sorted(missing):
    errors.append(f"missing schema: {name}")

for name in sorted(unexpected):
    errors.append(f"unexpected schema: {name}")

ids: set[str] = set()

for path in sorted(SCHEMA_DIR.glob("*.json")):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name}: invalid JSON: {exc}")
        continue

    if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{path.name}: JSON Schema draft must be 2020-12")

    schema_id = data.get("$id")
    if not schema_id:
        errors.append(f"{path.name}: missing $id")
    elif schema_id in ids:
        errors.append(f"{path.name}: duplicate $id: {schema_id}")
    else:
        ids.add(schema_id)

    if data.get("type") != "object":
        errors.append(f"{path.name}: root type must be object")

    if data.get("additionalProperties") is not False:
        errors.append(
            f"{path.name}: additionalProperties must be false at root"
        )

    if not data.get("required"):
        errors.append(f"{path.name}: required must not be empty")

if errors:
    print("FAIL V4 schema foundation")
    for error in errors:
        print(f"  - {error}")
    raise SystemExit(1)

print(
    "PASS V4 schema foundation: "
    f"{len(EXPECTED)} schemas present, valid JSON, "
    "unique IDs and closed root contracts"
)
