#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
WORKFLOWS = ROOT / ".github/workflows"
EXPECTED = {
    "v4-pr-quality.yml": "pr-quality",
    "v4-methodology.yml": "methodology",
    "v4-security-regression.yml": "security-regression",
    "v4-report-quality.yml": "report-quality",
    "v4-release-gate.yml": "release",
}
FORBIDDEN = ("terraform", "pull_request_target", "git push", "git tag", "gh release", "break-glass", "rollback", "promotion-stage")
ALLOWED_ACTIONS = ("actions/checkout@v4", "actions/setup-python@v5", "actions/upload-artifact@v4")


def main() -> int:
    errors: list[str] = []
    for name, profile in EXPECTED.items():
        path = WORKFLOWS / name
        if not path.is_file():
            errors.append(f"missing {name}")
            continue
        text = path.read_text(encoding="utf-8")
        try:
            document = yaml.safe_load(text)
        except Exception as exc:
            errors.append(f"{name}: invalid YAML: {exc}")
            continue
        if not isinstance(document, dict) or not document.get("jobs"):
            errors.append(f"{name}: jobs missing")
        permissions = document.get("permissions", {})
        if permissions != {"contents": "read"}:
            errors.append(f"{name}: permissions must be contents: read")
        expected_command = f"python tools/Invoke-V4FinalGates.py --profile {profile}"
        if expected_command not in text:
            errors.append(f"{name}: expected profile command missing")
        lowered = text.lower()
        for token in FORBIDDEN:
            if token in lowered:
                errors.append(f"{name}: forbidden capability token {token}")
        for action in re.findall(r"uses:\s*([^\s]+)", text):
            if action not in ALLOWED_ACTIONS:
                errors.append(f"{name}: unapproved action {action}")
    requirements = (ROOT / "requirements-v4.txt").read_text(encoding="utf-8")
    if "pypdf==6.21.2" not in requirements:
        errors.append("requirements-v4.txt must preserve approved pypdf==6.21.2 (KI-V4-001 remediation)")
    if errors:
        print(f"[FAIL] CP8 DevSecOps workflows: {len(errors)} error(s)")
        for error in errors: print(" - " + error)
        return 1
    print("[PASS] CP8 workflows: PR quality, methodology, security regression, report quality and release gate")
    return 0


if __name__ == "__main__": raise SystemExit(main())
