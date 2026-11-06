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

- Decision: **PENDING_INDEPENDENT_TEST**
- Publishable: **No** until authorized Git provenance/push, independent package testing and the checklist below are confirmed by the reviewer.

## Publication security review

- [ ] `assessment-result.v4.json` passes JSON Schema and semantic validation, including the optional action-card `basis` field.
- [ ] CHK-01..CHK-64 occur exactly once in evidence, observation, claim and control layers.
- [ ] Output digest and deterministic re-run match.
- [ ] Missing required evidence never yields an effective result.
- [ ] Evidence Coverage and Control Outcome remain independent.
- [ ] A missing configuration or missing evidence is never presented as a verified gap; only observed conditions are `FAIL`.
- [ ] Explicit adverse evidence (NonCompliant, Free tier, expired agent, missing export on a readable subscription) stays `FAIL`.
- [ ] An implicit collection scope is disclosed in the run log and in CHK-01, and never reported as full coverage of the estate.
- [ ] Scenarios driven only by not-verified controls do not reach the NOW horizon.
- [ ] Containment wording appears only on cards whose basis is `VERIFIED_GAP`.
- [ ] Proxy signals are not presented as direct product health or attack confirmation.
- [ ] `NOT_APPLICABLE` has an applicability reason and is not used to hide missing evidence.
- [ ] PARTIAL coverage is disclosed and does not silently become FULL.
- [ ] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [ ] CP6 HTML/JavaScript contains no risk, priority, scenario or roadmap calculation.
- [ ] EN-US and PT-BR embed the same canonical contract and the PT-BR summary labels and guidance are localized.
- [ ] Desktop/mobile Playwright checks pass without console errors or horizontal document overflow.
- [ ] EN-US/PT-BR PDFs are generated without browser header/footer leakage.
- [ ] The legacy v3.9.6 report and contract, Playwright, parity and PDF gates still pass.
- [ ] The five CP8 workflows parse and use `permissions: contents: read`.
- [ ] Workflow commands do not mutate source control or publish a release.
- [ ] Generated Python and PowerShell files pass syntax validation and PSScriptAnalyzer reports no Error/Warning for the collector.
- [ ] The gate entrypoint leaves the working tree exactly as found.
- [ ] Dependabot and dependency-review findings are reviewed.
- [ ] The 14 alerts raised against `pypdf==6.21.2` are confirmed closed after the upgrade to `pypdf==6.21.4` (KI-V4-001).
- [ ] `pypdf==6.21.4` resolves from the approved feed and all gates pass with the updated pin.
- [ ] Guide, README, CHANGELOG, collector, HTML pages and release notes all state v4.1.1 (`tools/Test-GuideVersion.py`).
- [ ] Release manifest and `SHA256SUMS` validate.

**Decision:** PENDING
