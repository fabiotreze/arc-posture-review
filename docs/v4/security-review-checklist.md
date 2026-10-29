# Arc Posture Review v4 security review checklist

Use this checklist for v4.0.0-rc.1 and repeat it before any stable release.

## Contract and traceability

- [ ] `assessment-result.v4.json` passes JSON Schema and semantic validation.
- [ ] CHK-01..CHK-64 occur exactly once in evidence, observation, claim and control layers.
- [ ] Output digest and deterministic re-run match.
- [ ] Missing required evidence never yields an effective result.
- [ ] Evidence Coverage and Control Outcome remain independent.

## False-positive review

- [ ] Every `INEFFECTIVE` and `AT_RISK` control has direct or explicitly bounded evidence.
- [ ] Proxy signals are not presented as direct product health or attack confirmation.
- [ ] `NOT_APPLICABLE` has an applicability reason and is not used to hide missing evidence.
- [ ] PARTIAL coverage is disclosed and does not silently become FULL.
- [ ] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [ ] `VALIDATED` means validated posture relevance, not validated exploitation.
- [ ] Before/after improvement comes from canonical `comparison.change=IMPROVED`.
- [ ] Regression and unchanged rows remain visible in the comparison table.

## Report quality

- [ ] CP6 HTML/JavaScript contains no risk, priority, scenario or roadmap calculation.
- [ ] `comparison: null` displays the no-baseline disclosure.
- [ ] EN-US and PT-BR embed the same canonical contract.
- [ ] Desktop/mobile Playwright checks pass without console errors or horizontal document overflow.
- [ ] EN-US/PT-BR PDFs are generated without browser header/footer leakage.
- [ ] The legacy v3.9.6 report and contract, Playwright, parity and PDF gates still pass.

## Repository and CI

- [ ] The five CP8 workflows parse and use `permissions: contents: read`.
- [ ] Workflow commands do not mutate source control or publish a release.
- [ ] Generated Python and PowerShell files pass syntax validation.
- [ ] The gate entrypoint leaves the working tree exactly as found.
- [ ] Commits created by the integration script are local only.

## Release blockers

- [ ] Dependabot and dependency-review findings are reviewed.
- [ ] The 11 alerts associated with `pypdf==6.19.0` are confirmed closed after the upgrade to `pypdf==6.21.2` (KI-V4-001).
- [ ] `pypdf==6.21.2` resolves from the approved feed and all gates pass with the updated pin.
- [ ] Stable v4.0.0 remains blocked until this security review is repeated and approved.
- [ ] Release manifest and `SHA256SUMS` validate.

Reviewer: ____________________  Date: ____________________  Decision: **PENDING / APPROVED / BLOCKED**
