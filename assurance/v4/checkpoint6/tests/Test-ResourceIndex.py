#!/usr/bin/env python3
"""CP6 resource index: contract, determinism, portal URL rule, rendering and runId guard."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "tests/fixtures/reviewed-lab-sanitized.zip"
CLI = ROOT / "assurance/v4/checkpoint5/cli/arc_posture.py"
RENDER = ROOT / "assurance/v4/checkpoint6/report/render_v4.py"
TOOL = ROOT / "tools/New-ResourceIndex.py"
PORTAL = "https://portal.azure.com/#@/resource/subscriptions/"


def run(*command: object) -> None:
    result = subprocess.run([sys.executable, *map(str, command)], cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)


def main() -> int:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        assessment, index_a, index_b = work / "a.json", work / "i1.json", work / "i2.json"
        run(CLI, "evaluate", "--evidence", FIXTURE, "--output", assessment)
        run(TOOL, "--evidence", FIXTURE, "--assessment", assessment, "--output", index_a)
        run(TOOL, "--evidence", FIXTURE, "--assessment", assessment, "--output", index_b)
        if index_a.read_bytes() != index_b.read_bytes():
            errors.append("resource index is not byte-deterministic")
        index = json.loads(index_a.read_text(encoding="utf-8"))
        document = json.loads(assessment.read_text(encoding="utf-8"))
        for key in ("contract", "generator", "runId", "packageSha256", "binding", "checks"):
            if key not in index:
                errors.append(f"resource index missing {key}")
        if index.get("contract") != "resource-index.v4" or index.get("runId") != document["metadata"]["runId"]:
            errors.append("resource index contract/runId drift")
        rows = [row for check in index.get("checks", {}).values() for row in check]
        for row in rows:
            rid, url = row.get("resourceId"), row.get("portalUrl")
            if rid and url != "https://portal.azure.com/#@/resource" + rid:
                errors.append(f"portal URL rule violated for {row.get('label')}")
            if not rid and url is not None:
                errors.append("portal URL without resourceId")
        html = work / "r.html"
        run(RENDER, "--input", assessment, "--output", html, "--locale", "en-US", "--resources", index_a)
        text = html.read_text(encoding="utf-8")
        outcomes = {row["checkId"]: row["outcome"] for row in document["controlAssessments"]}
        expected_links = [row["portalUrl"] for item in document["roadmap"]["NOW"] for cid in item["controlIds"]
                          if outcomes.get(cid) in ("INEFFECTIVE", "AT_RISK")
                          for row in index["checks"].get(cid, [])[:25] if row.get("portalUrl")]
        for url in expected_links:
            if url.replace("&", "&amp;") not in text:
                errors.append(f"portal link missing in report: {url}")
        if 'data-resource-index="unbound"' in text:
            errors.append("bound index rendered as unbound")
        tampered = dict(index, runId="ER-TAMPERED")
        bad_index = work / "bad.json"
        bad_index.write_text(json.dumps(tampered), encoding="utf-8")
        bad_html = work / "bad.html"
        run(RENDER, "--input", assessment, "--output", bad_html, "--locale", "pt-BR", "--resources", bad_index)
        bad = bad_html.read_text(encoding="utf-8")
        if expected_links and 'data-resource-index="unbound"' not in bad:
            errors.append("runId mismatch did not trigger the unbound warning")
        if PORTAL in bad:
            errors.append("portal links rendered from an unbound index")
        plain = work / "plain.html"
        run(RENDER, "--input", assessment, "--output", plain, "--locale", "en-US")
        if "data-resource-index" in plain.read_text(encoding="utf-8"):
            errors.append("resource block rendered without --resources")
    if errors:
        print(f"[FAIL] CP6 resource index: {len(errors)} error(s)")
        for error in errors:
            print(" - " + error)
        return 1
    print(f"[PASS] CP6 resource index: deterministic, {len(rows)} rows, {len(expected_links)} NOW portal links, runId guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
