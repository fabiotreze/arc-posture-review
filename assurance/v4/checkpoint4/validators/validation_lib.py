from __future__ import annotations

import json
import sys
from pathlib import Path

CP4_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(CP4_ROOT))

from engine.repository_layout import (
    REPO_ROOT,
    CP3_DATA,
    REVIEWED_LAB_REPORT,
)

from engine.deterministic_engine import (
    digest,
    horizon_for,
    priority_for,
)

ROOT = CP4_ROOT
CP4 = CP4_ROOT
REPORT = REVIEWED_LAB_REPORT


def load(path: Path = REPORT):
    return json.loads(
        path.read_text(encoding="utf-8-sig")
    )


def cp3(name: str):
    return json.loads(
        (CP3_DATA / name).read_text(
            encoding="utf-8-sig"
        )
    )


def require(
    condition: bool,
    message: str,
    errors: list[str],
) -> None:
    if not condition:
        errors.append(message)


def finish(errors: list[str], label: str) -> int:
    if errors:
        print(
            f"[FAIL] {label}: "
            f"{len(errors)} error(s)"
        )

        for error in errors[:100]:
            print(" - " + error)

        return 1

    print(f"[PASS] {label}")

    return 0
