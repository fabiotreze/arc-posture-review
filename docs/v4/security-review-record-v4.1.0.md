# Arc Posture Review v4.1.0 — evidence-hardening review record

## Scope

- CHK-42, CHK-55, CHK-57, and CHK-63 evidence interpretation.
- Synthetic negative regression coverage.
- GitHub Release idempotent upsert behavior.
- Version alignment for v4.1.0.

## Preserved boundaries

- 64 checks and 11 scenarios.
- `assessment-result.v4` contract version `4.0.0`.
- Collector schema version 3.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: **PENDING_INDEPENDENT_TEST**
- Publishable: **No** until authorized Git provenance/push and independent package testing are confirmed.

## Publication security review

- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation.
- [x] CHK-01..CHK-64 occur exactly once in evidence, observation, claim and control layers.
- [x] Output digest and deterministic re-run match.
- [x] Missing required evidence never yields an effective result.
- [x] Evidence Coverage and Control Outcome remain independent.
- [x] Every `INEFFECTIVE` and `AT_RISK` control has direct or explicitly bounded evidence.
- [x] Proxy signals are not presented as direct product health or attack confirmation.
- [x] `NOT_APPLICABLE` has an applicability reason and is not used to hide missing evidence.
- [x] PARTIAL coverage is disclosed and does not silently become FULL.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] `VALIDATED` means validated posture relevance, not validated exploitation.
- [x] Before/after improvement comes from canonical `comparison.change=IMPROVED`.
- [x] Regression and unchanged rows remain visible in the comparison table.
- [x] CP6 HTML/JavaScript contains no risk, priority, scenario or roadmap calculation.
- [x] `comparison: null` displays the no-baseline disclosure.
- [x] EN-US and PT-BR embed the same canonical contract.
- [x] Desktop/mobile Playwright checks pass without console errors or horizontal document overflow.
- [x] EN-US/PT-BR PDFs are generated without browser header/footer leakage.
- [x] The legacy v3.9.6 report and contract, Playwright, parity and PDF gates still pass.
- [x] The five CP8 workflows parse and use `permissions: contents: read`.
- [x] Workflow commands do not mutate source control or publish a release.
- [x] Generated Python and PowerShell files pass syntax validation.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Commits created by the integration script are local only.
- [x] Dependabot and dependency-review findings are reviewed.
- [x] The 11 alerts associated with `pypdf==6.19.0` are confirmed closed after the upgrade to `pypdf==6.21.2` (KI-V4-001).
- [x] `pypdf==6.21.2` resolves from the approved feed and all gates pass with the updated pin.
- [x] Stable v4.0.0 remains blocked until this security review is repeated and approved.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** PENDING

