# Arc Posture Review v4.2.3 — repository cleanup patch candidate

**Status:** APPROVED_FOR_PUBLICATION — security review approved by Fabio Rodrigues Vieira Costa on 2026-11-06 (13/13). Tagging and publishing remain a separate, manual step.

## Changed

- **Workflows:** a pull request now runs two jobs (`v4 PR quality`, which runs the full `release` gate profile and the browser app regression once, and `analyze` for PSScriptAnalyzer). The weekly `v4 security regression` stays; `v4 methodology`, `v4 report quality`, `v4 release gate` and the legacy `Report quality` were redundant subsets and are removed.
- **Code:** orphan scripts and the checkpoint 1 folders only they used are removed; the evidence-availability negative test is now part of the gate; nine duplicated schemas are gone (checkpoint 4 uses the checkpoint 5 copy, keeping only the two schemas that differ); PowerShell wrappers around Python entry points are removed; one `requirements-dev.txt` replaces two overlapping requirement files; unused imports and constants removed.
- **Quality gate:** `tools/Test-CodeQuality.py` runs ruff (pyflakes rules, `ruff.toml`) and fails on scripts that nothing runs or mentions.

## Preserved

- Collector logic, results, 64 checks and 11 scenarios, canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
