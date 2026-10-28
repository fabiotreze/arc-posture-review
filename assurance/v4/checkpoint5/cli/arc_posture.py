#!/usr/bin/env python3
"""Canonical Arc Posture Review v4 CLI: evaluate and compare."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
CP5 = REPO_ROOT / "assurance" / "v4" / "checkpoint5"
if str(CP5) not in sys.path:
    sys.path.insert(0, str(CP5))

from engine.canonical_v4 import (  # noqa: E402
    EvaluationError,
    build_comparison,
    evaluate_path,
    read_assessment,
    write_json,
)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="arc-posture", description="Arc Posture Review canonical v4 CLI")
    commands = root.add_subparsers(dest="command", required=True)

    evaluate = commands.add_parser("evaluate", help="Run collector -> engine -> assessment-result.v4.json")
    evaluate.add_argument("--evidence", required=True, help="Collector results.json or evidence ZIP (schemaVersion 3)")
    evaluate.add_argument("--baseline", help="Optional prior collector results.json or evidence ZIP")
    evaluate.add_argument("--output", default="assessment-result.v4.json", help="Canonical assessment output")

    compare = commands.add_parser("compare", help="Compare two canonical assessment-result.v4.json files")
    compare.add_argument("--before", required=True, help="Baseline assessment-result.v4.json")
    compare.add_argument("--after", required=True, help="Current assessment-result.v4.json")
    compare.add_argument("--output", default="assessment-comparison.v4.json", help="Canonical comparison output")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "evaluate":
            result = evaluate_path(args.evidence, args.baseline)
            write_json(result, args.output)
            print(f"[PASS] evaluate {result['metadata']['runId']} -> {Path(args.output)}")
            return 0
        before = read_assessment(args.before)
        after = read_assessment(args.after)
        comparison = build_comparison(before, after)
        write_json(comparison, args.output)
        print(f"[PASS] compare {comparison['baselineRunId']} -> {comparison['currentRunId']} -> {Path(args.output)}")
        return 0
    except (EvaluationError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"[FAIL] {args.command}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
