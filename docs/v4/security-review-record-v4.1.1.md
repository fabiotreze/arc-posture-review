# Arc Posture Review v4.1.1 — posture versus evidence review record

## Scope

- Wording and result semantics for CHK-01, CHK-18, CHK-23, CHK-31, CHK-33, CHK-41, CHK-43, CHK-45 and CHK-56 (see `docs/v4.1.1-posture-vs-evidence.md`).
- Engine: scenario cap for not-verified controls, defense status, action-card `basis`.
- v4 report: executive summary, vocabulary and action plan.
- `pypdf` pin moved to `6.21.4` (KI-V4-001).
- Version alignment for v4.1.1.

## Preserved boundaries

- 64 checks and 11 scenarios.
- `assessment-result.v4` contract version `4.0.0`.
- Collector schema version 3.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: **APPROVED** by Fabio Rodrigues Vieira Costa. The approval was recorded by the assistant on the reviewer's explicit instruction on 2026-11-06, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer passed.
- Publishable: **Yes**. Provenance and the independent test blockers are cleared by this decision; tagging, pushing and publishing remain a separate manual step, and the release workflow re-verifies the manifest and `SHA256SUMS` on the tag.

## Publication security review

- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation, including the optional action-card `basis` field.
- [x] CHK-01..CHK-64 occur exactly once in evidence, observation, claim and control layers.
- [x] Output digest and deterministic re-run match.
- [x] Missing required evidence never yields an effective result.
- [x] Evidence Coverage and Control Outcome remain independent.
- [x] A missing configuration or missing evidence is never presented as a verified gap; only observed conditions are `FAIL`.
- [x] Explicit adverse evidence (NonCompliant, Free tier, expired agent, missing export on a readable subscription) stays `FAIL`.
- [x] An implicit collection scope is disclosed in the run log and in CHK-01, and never reported as full coverage of the estate.
- [x] Scenarios driven only by not-verified controls do not reach the NOW horizon.
- [x] Containment wording appears only on cards whose basis is `VERIFIED_GAP`.
- [x] Proxy signals are not presented as direct product health or attack confirmation.
- [x] `NOT_APPLICABLE` has an applicability reason and is not used to hide missing evidence.
- [x] PARTIAL coverage is disclosed and does not silently become FULL.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] CP6 HTML/JavaScript contains no risk, priority, scenario or roadmap calculation.
- [x] EN-US and PT-BR embed the same canonical contract and the PT-BR summary labels and guidance are localized.
- [x] Desktop/mobile Playwright checks pass without console errors or horizontal document overflow.
- [x] EN-US/PT-BR PDFs are generated without browser header/footer leakage.
- [x] The legacy v3.9.6 report and contract, Playwright, parity and PDF gates still pass.
- [x] The five CP8 workflows parse and use `permissions: contents: read`.
- [x] Workflow commands do not mutate source control or publish a release.
- [x] Generated Python and PowerShell files pass syntax validation and PSScriptAnalyzer reports no Error/Warning for the collector.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Dependabot and dependency-review findings are reviewed.
- [x] `pypdf==6.21.4` is the first patched version for the 14 alerts raised against `pypdf==6.21.2` (KI-V4-001); Dependabot confirms closure after the merge.
- [x] `pypdf==6.21.4` resolves from the approved feed and all gates pass with the updated pin.
- [x] Guide, README, CHANGELOG, collector, HTML pages and release notes all state v4.1.1 (`tools/Test-GuideVersion.py`).
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (28/28)
