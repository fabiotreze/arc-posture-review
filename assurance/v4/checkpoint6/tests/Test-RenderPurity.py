#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RENDERER = ROOT / "assurance/v4/checkpoint6/report/render_v4.py"


def main() -> int:
    source = RENDERER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    errors: list[str] = []
    forbidden_tokens = ["priority_for(", "risk_level(", "horizon_for(", "_scenario_evaluations(", "DeterministicEvaluationEngine(", "load_evidence("]
    for token in forbidden_tokens:
        if token in source:
            errors.append(f"forbidden Evaluation Engine calculation in renderer: {token}")
    render_function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "render")
    for node in ast.walk(render_function):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, (ast.Subscript, ast.Attribute)):
                    errors.append(f"renderer mutates an object at line {node.lineno}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"sum", "max", "min"}:
            errors.append(f"renderer aggregates canonical values at line {node.lineno}")
    js_start = source.index('JS = r"""')
    js_end = source.index('"""', js_start + len('JS = r"""'))
    js = source[js_start:js_end]
    for token in ("JSON.parse", "canonical-assessment", "residualRisk", "priorityScore", "securityScenarios"):
        if token in js:
            errors.append(f"browser runtime interprets canonical data: {token}")
    if errors:
        print(f"[FAIL] render purity: {len(errors)} error(s)")
        for error in errors:
            print(" - " + error)
        return 1
    print("[PASS] render purity: no risk, priority, scenario or roadmap calculation in HTML/JavaScript renderer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
