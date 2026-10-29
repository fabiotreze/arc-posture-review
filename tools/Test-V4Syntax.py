#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPES = [ROOT / "assurance/v4/checkpoint6", ROOT / "assurance/v4/checkpoint7", ROOT / "assurance/v4/checkpoint8", ROOT / "assurance/v4/checkpoint9", ROOT / "assurance/v4/checkpoint10", ROOT / "tools"]


def main() -> int:
    errors: list[str] = []
    python_files = sorted({path for scope in SCOPES if scope.exists() for path in scope.rglob("*.py") if path.name in {"Invoke-V4FinalGates.py", "Test-V4Syntax.py"} or "checkpoint" in str(path)})
    for path in python_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    workflows = sorted((ROOT / ".github/workflows").glob("v4-*.yml"))
    if len(workflows) != 5:
        errors.append(f"expected five v4 workflows, found {len(workflows)}")
    if errors:
        print(f"[FAIL] v4 syntax inventory: {len(errors)} error(s)")
        for error in errors: print(" - " + error)
        return 1
    print(f"[PASS] Python syntax ({len(python_files)} files) and workflow inventory ({len(workflows)} files)")
    return 0


if __name__ == "__main__": raise SystemExit(main())
