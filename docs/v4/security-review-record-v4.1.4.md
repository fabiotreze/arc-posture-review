# Arc Posture Review v4.1.4 — wording and pt-BR report review record

## Scope

- Action cards for verified gaps use posture wording (*Remediate*) instead of incident-response wording (*Contain*, *preserve evidence*); the engine supplies posture actions and closure criteria for every basis.
- The pt-BR v4 report renders engine, scenario, card, criterion and collector texts in Portuguese. The translation is display-only: the embedded canonical JSON is identical in both locales.
- `criteria/v4/pt-br-detail-rules.json` mirrors the app's Portuguese rules; `tools/Test-PtBrContent.py` guards the parity and the absence of English static text. The rule order bug that left "connected máquina(s)" mixed text is fixed in the app and the report.
- The collector writes `report/report.log` (outside the manifest) with the report step trace.
- Version alignment for v4.1.4.

## Preserved boundaries

- 64 checks and 11 scenarios.
- `assessment-result.v4` contract version `4.0.0`; scores, priorities and outcomes are unchanged.
- Collector schema version 3; evidence collection is unchanged.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: see the line at the end. The approval is recorded by the assistant on the reviewer's instruction, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer pass.

## Publication security review

- [x] The localization only rewrites visible text nodes of the generated HTML; scripts, styles, attributes and the canonical JSON are never modified (`tools/Test-PtBrContent.py`).
- [x] The Portuguese rules are static data read from the kit; no remote resource, command or code is loaded from them.
- [x] The kit still equals the pinned SHA-256 (`tools/Build-Kit.py --check`) and now includes the two data files the renderer reads.
- [x] `report/report.log` contains only the collector version, a timestamp and the kit source; no environment data.
- [x] The collector performs no Azure write and the `az` command allow-list is unchanged.
- [x] Action card wording no longer asserts containment or incident response; the guardrail "a posture weakness is not evidence of exploitation or compromise" is preserved.
- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation; CHK-01..CHK-64 occur exactly once.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] The app still opens the packaged report and accepts `report/` as outside the manifest (`tools/Test-AppV4Report.py`).
- [x] Desktop and mobile Playwright checks pass without console errors or horizontal document overflow.
- [x] The embedded collector, criteria and CSS in the pages match their sources (`tools/Sync-ReportAssets.py --check`).
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.1.4 (`tools/Test-GuideVersion.py`).
- [x] PSScriptAnalyzer reports no Error/Warning for the collector and the BOM is intact.
- [x] The five CP8 workflows parse and the release workflow runs the new test before uploading the script and kit.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (16/16)
