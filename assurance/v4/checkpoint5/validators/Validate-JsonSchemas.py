#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    print("[FAIL] install assurance/v4/checkpoint5/requirements.txt")
    raise SystemExit(1)

CP5 = Path(__file__).resolve().parents[1]
SCHEMAS = {path.name: json.loads(path.read_text(encoding="utf-8-sig")) for path in (CP5 / "schemas").glob("*.json")}
REGISTRY = Registry()
for name, schema in SCHEMAS.items():
    REGISTRY = REGISTRY.with_resource(name, Resource.from_contents(schema))

instances = [
    ("assessment-result.v4.schema.json", CP5 / "reports" / "assessment-result.v4.json"),
    ("assessment-comparison.v4.schema.json", CP5 / "reports" / "assessment-comparison.v4.json"),
]
errors = []
for schema_name, path in instances:
    instance = json.loads(path.read_text(encoding="utf-8-sig"))
    validator = Draft202012Validator(SCHEMAS[schema_name], registry=REGISTRY)
    for error in validator.iter_errors(instance):
        errors.append((schema_name, error))
errors.sort(key=lambda item: (item[0], list(item[1].absolute_path)))
if errors:
    print(f"[FAIL] Checkpoint 5 JSON Schemas: {len(errors)} error(s)")
    for schema_name, error in errors[:100]:
        print(" - " + schema_name + ":" + "/".join(map(str, error.absolute_path)) + ": " + error.message)
    raise SystemExit(1)
print("[PASS] Checkpoint 5 JSON Schemas: assessment-result.v4 and assessment-comparison.v4")
