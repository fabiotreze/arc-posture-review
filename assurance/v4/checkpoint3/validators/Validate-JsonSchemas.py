from pathlib import Path
import json
import sys

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    print('[FAIL] JSON Schema validator requires: python -m pip install -r checkpoint3-v4/requirements.txt')
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
schemas = {p.name: json.loads(p.read_text(encoding='utf-8-sig')) for p in (ROOT / 'schemas').glob('*.json')}
registry = Registry()
for name, schema in schemas.items():
    registry = registry.with_resource(name, Resource.from_contents(schema))

pairs = [
    ('enriched-check.schema.json', 'checks.enriched.json'),
    ('control-assessment.schema.json', 'control-assessments.json'),
    ('defense-coverage.schema.json', 'defense-coverage.json'),
    ('security-scenario.schema.json', 'security-scenarios.json'),
]
errors = []
for schema_name, data_name in pairs:
    validator = Draft202012Validator(schemas[schema_name], registry=registry)
    rows = json.loads((ROOT / 'data' / data_name).read_text(encoding='utf-8-sig'))
    row_errors = []
    for index, row in enumerate(rows):
        for error in validator.iter_errors(row):
            row_errors.append(f'{data_name}[{index}]: {error.message}')
    if row_errors:
        errors.extend(row_errors)
        print(f'[FAIL] {schema_name}: {len(row_errors)} error(s)')
    else:
        print(f'[PASS] {schema_name}: {len(rows)} row(s)')

if errors:
    for error in errors[:100]:
        print(' - ' + error)
    raise SystemExit(1)
print('[PASS] JSON Schemas Draft 2020-12')
