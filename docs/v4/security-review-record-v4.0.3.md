# Arc Posture Review v4.0.3 security review record

Use this checklist for the v4.0.3 evidence-availability patch before publication.

## Contract and traceability

- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation.
- [x] CHK-01..CHK-64 occur exactly once in evidence, observation, claim and control layers.
- [x] Output digest and deterministic re-run match.
- [x] Missing required evidence never yields an effective result.
- [x] Evidence Coverage and Control Outcome remain independent.

## False-positive review

- [x] Every `INEFFECTIVE` and `AT_RISK` control has direct or explicitly bounded evidence.
- [x] Proxy signals are not presented as direct product health or attack confirmation.
- [x] `NOT_APPLICABLE` has an applicability reason and is not used to hide missing evidence.
- [x] PARTIAL coverage is disclosed and does not silently become FULL.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] `VALIDATED` means validated posture relevance, not validated exploitation.
- [x] Before/after improvement comes from canonical `comparison.change=IMPROVED`.
- [x] Regression and unchanged rows remain visible in the comparison table.

## Report quality

- [x] CP6 HTML/JavaScript contains no risk, priority, scenario or roadmap calculation.
- [x] `comparison: null` displays the no-baseline disclosure.
- [x] EN-US and PT-BR embed the same canonical contract.
- [x] Desktop/mobile Playwright checks pass without console errors or horizontal document overflow.
- [x] EN-US/PT-BR PDFs are generated without browser header/footer leakage.
- [x] The legacy v3.9.6 report and contract, Playwright, parity and PDF gates still pass.

## Repository and CI

- [x] The five CP8 workflows parse and use `permissions: contents: read`.
- [x] Workflow commands do not mutate source control or publish a release.
- [x] Generated Python and PowerShell files pass syntax validation.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Commits created by the integration script are local only.

## Release blockers

- [x] Dependabot and dependency-review findings are reviewed.
- [x] The 11 alerts associated with `pypdf==6.19.0` are confirmed closed after the upgrade to `pypdf==6.21.2` (KI-V4-001).
- [x] `pypdf==6.21.2` resolves from the approved feed and all gates pass with the updated pin.
- [x] Stable v4.0.3 remains blocked until this security review is repeated and approved.
- [x] Release manifest and `SHA256SUMS` validate.

## v4.0.3 evidence

- Base: v4.0.2 (`b84d087`). Changes are limited to the evidence-availability check, a negative test, version metadata and documentation.
- `tools/Invoke-V4FinalGates.py` profiles `release` and `all`: PASS. Regression (syntax, zero-target, report contract, lab corrections, Playwright, checkpoint 4 gates): PASS.
- Pull request CI (methodology, pr-quality, report-quality, security-regression, analyze, PSScriptAnalyzer): PASS.
- Real-environment validation and record corrections: `docs/v4/security-review-addendum-v4.0.3.md`.

Reviewer: Fabio Rodrigues Vieira Costa Date: 2026-10-30 Decision: PENDING


## Zero-target hotfix validation

- [x] An empty, successfully collected Azure Arc machine inventory does not result in PASS for machine-dependent controls.
- [x] CHK-12, CHK-21, CHK-23, CHK-24, CHK-27, CHK-28, CHK-32, CHK-37, CHK-39 and CHK-51 return INFO, FULL evidence coverage and found=0 when the Azure Arc inventory is empty.
- [x] The zero-target disclosure explicitly states that the control was not evaluated and must not be interpreted as PASS.
- [x] The zero-target regression test passes.
- [x] The standalone and embedded collectors remain synchronized.
