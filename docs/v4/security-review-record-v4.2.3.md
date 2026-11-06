# Arc Posture Review v4.2.3 — repository cleanup review record

## Scope

- Workflows reduced to `v4 PR quality` (release profile plus the browser app regression and the PDF matrix), `v4 security regression` (weekly) and the existing `PSScriptAnalyzer` and `Release`; `tools/Invoke-V4FinalGates.py` keeps the profiles `release` and `security-regression`.
- Orphan scripts removed (`Build-V4Taxonomy.py`, `Test-V4Taxonomy.py`, `Test-V4Schema.py`, `Test-V4Mapping.py`, `Test-ZeroTargetControls.py`) with the checkpoint 1 folders `taxonomy/`, `schemas/` and `security-scenarios/`; `Test-EvidenceAvailability.py` (a security negative test) is wired into the gate instead of removed.
- Nine duplicated checkpoint 4 schemas removed (checkpoint 4 reads the checkpoint 5 copy and keeps the two that differ); PowerShell wrappers (`arc-posture.ps1`, `Invoke-AssessmentPipeline.ps1`, the checkpoint 4 and 5 `Invoke-AllGates.ps1`, `tools/New-V4Report.ps1`) removed; `requirements-v4.txt` merged into `requirements-dev.txt`; unused imports and constants removed.
- `tools/Test-CodeQuality.py` and `ruff.toml` added.
- Version alignment for v4.2.3.

## Preserved boundaries

- Collector logic and results are unchanged; 64 checks and 11 scenarios; `assessment-result.v4` contract version `4.0.0`; collector schema version 3.
- The workflows keep `contents: read`, the approved action set and no mutating release action (`Test-DevSecOpsWorkflows.py`).
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: see the line at the end. The approval is recorded by the assistant on the reviewer's instruction, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer pass.

## Publication security review

- [x] No security test was removed: the evidence-availability negative test is now part of the gate and the removed tests covered superseded checkpoint 1 artifacts.
- [x] The pull request workflow runs the same gates as before (the release profile is a superset of the removed profiles); the weekly security regression is kept.
- [x] Workflows keep `contents: read` and only approved actions (`assurance/v4/checkpoint8/tests/Test-DevSecOpsWorkflows.py`).
- [x] The pypdf pin `pypdf==6.21.4` is preserved in the merged `requirements-dev.txt`.
- [x] The kit still equals the pinned SHA-256 (`tools/Build-Kit.py --check`).
- [x] The collector logic is unchanged and performs no Azure write.
- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation; CHK-01..CHK-64 occur exactly once.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.2.3 (`tools/Test-GuideVersion.py`).
- [x] PSScriptAnalyzer reports no Error/Warning for the collector and the BOM is intact.
- [x] The embedded collector, criteria and CSS in the pages match their sources (`tools/Sync-ReportAssets.py --check`).
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (13/13)
