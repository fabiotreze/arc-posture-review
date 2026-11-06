# Arc Posture Review v4.1.5 — pt-BR rendering fix review record

## Scope

- The pt-BR rules of the v4 report no longer match inside words: "controle(s)" was rewritten to "contpapel(is)" by the `role(s)` rule in the executive summary and the PARTIAL coverage sentence of v4.1.4. Rules that start with a letter now require a word boundary; `tools/Test-PtBrContent.py` guards it.
- README (EN-US/PT-BR), known issues and the pt-BR README screenshot refreshed for the current behaviour.
- Version alignment for v4.1.5.

## Preserved boundaries

- 64 checks and 11 scenarios; scores, priorities and outcomes unchanged.
- `assessment-result.v4` contract version `4.0.0`; the embedded canonical JSON is identical in both locales.
- Collector schema version 3; evidence collection and the collector logic are unchanged.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: see the line at the end. The approval is recorded by the assistant on the reviewer's instruction, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer pass.

## Publication security review

- [x] The localization only rewrites visible text nodes; scripts, styles, attributes and the canonical JSON are never modified, and the canonical English text stays in the tooltip (`tools/Test-PtBrContent.py`, report contract).
- [x] The word-boundary guard only narrows what the static rules match; no new rule, command or remote resource is added.
- [x] The kit still equals the pinned SHA-256 (`tools/Build-Kit.py --check`).
- [x] The collector performs no Azure write and the `az` command allow-list is unchanged.
- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation; CHK-01..CHK-64 occur exactly once.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] README and known issues describe the real behaviour and contain no environment data.
- [x] README screenshots are generated from the sanitized fixture only.
- [x] Desktop and mobile Playwright checks pass without console errors or horizontal document overflow.
- [x] The embedded collector, criteria and CSS in the pages match their sources (`tools/Sync-ReportAssets.py --check`).
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.1.5 (`tools/Test-GuideVersion.py`).
- [x] PSScriptAnalyzer reports no Error/Warning for the collector and the BOM is intact.
- [x] The five CP8 workflows parse; the release workflow uploads the script and kit only after the gates pass.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (15/15)
