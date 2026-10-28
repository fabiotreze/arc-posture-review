from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CP4 = ROOT / "checkpoint4-v4"
REPORT = CP4 / "reports" / "reviewed-lab-evaluation.json"
sys.path.insert(0, str(CP4))
from engine.deterministic_engine import digest, horizon_for, priority_for


def load(path: Path = REPORT):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def cp3(name: str):
    return json.loads((ROOT / "checkpoint3-v4" / "data" / name).read_text(encoding="utf-8-sig"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def finish(errors: list[str], label: str) -> int:
    if errors:
        print(f"[FAIL] {label}: {len(errors)} error(s)")
        for error in errors[:100]:
            print(" - " + error)
        return 1
    print(f"[PASS] {label}")
    return 0
