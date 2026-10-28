#!/usr/bin/env python3
from test_lib import *


def main() -> int:
    first = canonical(); second = canonical(); errors = []
    if canonical_text(first).encode("utf-8") != canonical_text(second).encode("utf-8"): errors.append("output bytes differ")
    if first["metadata"]["runId"] != second["metadata"]["runId"]: errors.append("run IDs differ")
    if first["outputDigest"] != second["outputDigest"]: errors.append("digests differ")
    if errors:
        print("[FAIL] canonical determinism: " + ", ".join(errors)); return 1
    print(f"[PASS] canonical determinism: byte-identical {first['metadata']['runId']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
