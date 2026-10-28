#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "checkpoint4-v4"))
from engine.deterministic_engine import DeterministicEvaluationEngine, EvaluationError, load_evidence, write_evaluation


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic Checkpoint 4 Evaluation Engine.")
    parser.add_argument("--evidence", required=True, help="Collector results.json or evidence ZIP")
    parser.add_argument("--baseline", help="Optional prior results.json or evidence ZIP for before/after")
    parser.add_argument("--output", required=True, help="Output evaluation JSON")
    args = parser.parse_args()
    try:
        engine = DeterministicEvaluationEngine(ROOT)
        current = load_evidence(args.evidence)
        baseline = load_evidence(args.baseline) if args.baseline else None
        result = engine.evaluate(current, baseline)
        write_evaluation(result, args.output)
    except (EvaluationError, OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] Evaluation Engine: {exc}")
        return 1
    print(f"[PASS] Evaluation Engine: {result['runId']} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
