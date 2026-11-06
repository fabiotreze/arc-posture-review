# Arc Posture Review v4.2.1 — pt-BR rule table fix review record

## Scope

- In v4.2.0 the Portuguese rules for the new CHK-21 and CHK-29 sentences were written into the wrong place of the app file, so the Portuguese v4 report showed those two sentences mostly in English (found in the first real run of v4.2.0). They are now in the `PT_DETAIL_RULES` table and in `criteria/v4/pt-br-detail-rules.json`.
- `tools/Test-PtBrContent.py` gained golden sentences taken from a real run (CHK-21, CHK-29, CHK-33): each must be rendered in Portuguese.
- Version alignment for v4.2.1.

## Preserved boundaries

- 64 checks and 11 scenarios; `assessment-result.v4` contract version `4.0.0`; collector schema version 3; collector logic unchanged.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: see the line at the end. The approval is recorded by the assistant on the reviewer's instruction, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer pass.

## Publication security review

- [x] Only display rules changed; the embedded canonical JSON of the report is untouched (`tools/Test-PtBrContent.py`).
- [x] The kit still equals the pinned SHA-256 (`tools/Build-Kit.py --check`).
- [x] The collector performs no Azure write and the `az` command allow-list is unchanged.
- [x] The embedded collector, criteria and CSS in the pages match their sources (`tools/Sync-ReportAssets.py --check`).
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.2.1 (`tools/Test-GuideVersion.py`).
- [x] PSScriptAnalyzer reports no Error/Warning for the collector and the BOM is intact.
- [x] The five CP8 workflows parse; the release workflow uploads the script and kit only after the gates pass.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (9/9)
