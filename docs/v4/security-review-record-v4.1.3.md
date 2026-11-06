# Arc Posture Review v4.1.3 — app redesign review record

## Scope

- The browser app (EN-US and PT-BR) gains a verdict at the top of the Analysis, a Start here page and search in the Guide, and a refreshed theme (`tools/report-ux.js`, `tools/report-responsive.css`, synced by `tools/Sync-ReportAssets.py`).
- The collection wizard defaults to the subscription list; the current-subscription mode stays available with a warning.
- Version alignment for v4.1.3.

## Preserved boundaries

- 64 checks and 11 scenarios.
- `assessment-result.v4` contract version `4.0.0`.
- Collector schema version 3; collector logic is unchanged apart from the version.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: see the line at the end. The approval is recorded by the assistant on the reviewer's instruction, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer pass.

## Publication security review

- [x] The new JavaScript builds the verdict and the guide start page from text and numbers already in the page; values are escaped with `esc()` before insertion and no remote resource is loaded.
- [x] The Content-Security-Policy of the app and of the saved analysis is unchanged (`tools/Test-ReportVisual.py`, `tools/Test-ReportContract.py`).
- [x] The collector performs no Azure write and the `az` command allow-list is unchanged.
- [x] The runtime kit still equals the pinned SHA-256 (`tools/Build-Kit.py --check`).
- [x] The app still opens the packaged report only from the loaded `.zip` and applies *Hide e-mails* when saving (`tools/Test-AppV4Report.py`).
- [x] Verdict and action wording keeps the posture vocabulary: Verified gap, Improvement opportunity, Not verified (`tools/Test-PostureWording.py`).
- [x] Desktop and mobile Playwright checks pass without console errors or horizontal document overflow.
- [x] The embedded collector, criteria and CSS in the pages match their sources (`tools/Sync-ReportAssets.py --check`).
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.1.3 (`tools/Test-GuideVersion.py`).
- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation; CHK-01..CHK-64 occur exactly once.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] The five CP8 workflows parse and the release workflow uploads the script and `arc-posture-kit.zip` only after the gates pass.
- [x] PSScriptAnalyzer reports no Error/Warning for the collector.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (15/15)
