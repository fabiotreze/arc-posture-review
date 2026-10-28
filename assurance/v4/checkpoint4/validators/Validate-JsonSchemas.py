#!/usr/bin/env python3
from pathlib import Path
import json

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    print("[FAIL] install checkpoint4-v4/requirements.txt")
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
schemas = {p.name: json.loads(p.read_text(encoding="utf-8-sig")) for p in (ROOT / "schemas").glob("*.json")}
registry = Registry()
for name, schema in schemas.items():
    registry = registry.with_resource(name, Resource.from_contents(schema))
report = json.loads((ROOT / "reports" / "reviewed-lab-evaluation.json").read_text(encoding="utf-8-sig"))

import sys
sys.path.insert(0, str(ROOT))
from engine.deterministic_engine import load_evidence
input_document = load_evidence(PROJECT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip").document

errors = []
for schema_name, instance in [
    ("collector-results-v3.schema.json", input_document),
    ("evaluation-run.schema.json", report),
]:
    validator = Draft202012Validator(schemas[schema_name], registry=registry)
    for error in validator.iter_errors(instance):
        errors.append((schema_name, error))
errors.sort(key=lambda item: (item[0], list(item[1].absolute_path)))
if errors:
    print(f"[FAIL] Checkpoint 4 JSON Schemas: {len(errors)} error(s)")
    for schema_name, error in errors[:100]:
        print(" - " + schema_name + ":" + "/".join(map(str, error.absolute_path)) + ": " + error.message)
    raise SystemExit(1)
print(f"[PASS] Checkpoint 4 JSON Schemas Draft 2020-12: input schema-v3, {len(report['controlAssessments'])} controls, {len(report['securityScenarios'])} scenarios")
