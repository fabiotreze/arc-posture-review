#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from test_lib import *
from engine.deterministic_engine import canonical_bytes, digest, write_evaluation


def main() -> int:
    evaluator = engine(); source = fixture(); failures = []
    first = evaluator.evaluate(source)
    second = evaluator.evaluate(source)
    if first != second:
        failures.append("same evidence and model produced different objects")
    if canonical_bytes(first) != canonical_bytes(second):
        failures.append("canonical bytes changed")
    if first["runId"] != second["runId"] or first["outputDigest"] != second["outputDigest"]:
        failures.append("stable identifiers changed")
    unsigned = {key: value for key, value in first.items() if key != "outputDigest"}
    if first["outputDigest"] != digest(unsigned):
        failures.append("output digest is not reproducible")
    with tempfile.TemporaryDirectory() as temp:
        one = Path(temp) / "one.json"; two = Path(temp) / "two.json"
        write_evaluation(first, one); write_evaluation(second, two)
        if one.read_bytes() != two.read_bytes():
            failures.append("serialized files are not byte-identical")
    forbidden = {"evaluatedNow", "currentTime", "randomSeed"}
    if forbidden & set(first):
        failures.append("nondeterministic runtime field introduced")
    if failures:
        print(f"[FAIL] determinism: {len(failures)} error(s)")
        for item in failures: print(" - " + item)
        return 1
    print(f"[PASS] determinism: byte-identical output, stable {first['runId']} and reproducible digest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
