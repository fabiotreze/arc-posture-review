# Arc Posture Review v4.1.2 — single package review record

## Scope

- The collector adds the canonical v4 report to the evidence `.zip` (`report/`), with a pinned-SHA-256 runtime kit when it does not run from a clone (see `docs/v4.1.2-single-package.md`).
- The app opens and saves the packaged report.
- README, guide and in-app notes corrected to the real flow.
- Version alignment for v4.1.2.

## Preserved boundaries

- 64 checks and 11 scenarios.
- `assessment-result.v4` contract version `4.0.0`.
- Collector schema version 3.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: **APPROVED** by Fabio Rodrigues Vieira Costa. The approval was recorded by the assistant on the reviewer's instruction on 2026-11-06, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer passed.
- Publishable: **Yes**. Provenance and the independent test blockers are cleared by this decision. The download of the kit from the published release can only be exercised after publication: it is covered before that by the local-path acceptance and hash-mismatch tests, and is confirmed by one collector run in Cloud Shell right after the release.

## Publication security review

- [x] The collector performs no Azure write: the report step runs locally, the `az` command allow-list is unchanged.
- [x] A downloaded kit is executed only when its SHA-256 equals `$KitSha256`; a mismatch aborts the report step (`tools/Test-V4ReportStep.py`).
- [x] `tools/Build-Kit.py --check` fails when the pinned value is stale, in the checkpoint 4 gate and in the release workflow.
- [x] The kit contains only stdlib Python and data files, makes no network or process call and writes only the output files it is given (temporary work folder and `report/`).
- [x] A failure of the report step (no Python, no network, hash mismatch) leaves a complete evidence package, removes any partial `report/` and does not stop the collection.
- [x] `manifest.json` still lists and verifies every evidence file; `report/` is the only folder the app treats as outside the manifest.
- [x] The app opens the packaged report only from the loaded `.zip`, applies *Hide e-mails* when saving and shows the buttons only when `report/` exists (`tools/Test-AppV4Report.py`).
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.1.2 and the real flow (`tools/Test-GuideVersion.py`).
- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation; CHK-01..CHK-64 occur exactly once.
- [x] Missing required evidence never yields an effective result; Evidence Coverage and Control Outcome remain independent.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] CP6 HTML/JavaScript contains no risk, priority, scenario or roadmap calculation.
- [x] Desktop/mobile Playwright checks pass without console errors or horizontal document overflow.
- [x] The legacy v3.9.6 report and contract, parity and PDF gates still pass.
- [x] The five CP8 workflows parse; the release workflow uploads the script and `arc-posture-kit.zip` and only after the gates pass.
- [x] PSScriptAnalyzer reports no Error/Warning for the collector.
- [x] Dependabot and dependency-review findings are reviewed (`pypdf==6.21.4`).
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (19/19)
