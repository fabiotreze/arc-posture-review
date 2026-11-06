# Arc Posture Review v4.1.6 — fidelity fixes review record

## Scope

- **CHK-21:** the check labelled any open agent port as SSH/Windows Admin Center. It now classifies 22 (SSH), 3389 (RDP) and 6516 (Windows Admin Center) and reports every other port as unclassified, with the per-machine split in the findings (`managementChannels`, `unclassifiedPorts`). The status stays WARN and the wording says an open port is a posture item, not evidence of exposure.
- **CHK-33:** `machines` counted distinct resource IDs below `/machines/`, so nested resources (for example SQL Server objects) inflated it above the number of Arc machines. The query now reduces each ID to its machine before counting.
- Community files (`CONTRIBUTING.md`, issue and pull request templates) and `tools/Sync-PtRules.py`.
- Version alignment for v4.1.6.

## Preserved boundaries

- 64 checks and 11 scenarios; `assessment-result.v4` contract version `4.0.0`; collector schema version 3.
- The collector stays read-only: the Resource Graph query only adds a projection, the port classification runs locally on collected data, and the `az` command allow-list is unchanged.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: see the line at the end. The approval is recorded by the assistant on the reviewer's instruction, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer pass.

## Publication security review

- [x] The CHK-21 classification parses the collected port list with a numeric regular expression; it executes nothing and writes nothing to Azure.
- [x] The CHK-33 change is a read-only Azure Resource Graph projection (`extract`) inside the same query.
- [x] The kit still equals the pinned SHA-256 (`tools/Build-Kit.py --check`).
- [x] The collector performs no Azure write and the `az` command allow-list is unchanged.
- [x] Issue and pull request templates ask not to attach collected data and point vulnerabilities to private reporting.
- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation; CHK-01..CHK-64 occur exactly once.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] The pt-BR rule for the new CHK-21 text is in the app table and in `criteria/v4/pt-br-detail-rules.json` (`tools/Test-PtBrContent.py`).
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.1.6 (`tools/Test-GuideVersion.py`).
- [x] PSScriptAnalyzer reports no Error/Warning for the collector and the BOM is intact.
- [x] The embedded collector, criteria and CSS in the pages match their sources (`tools/Sync-ReportAssets.py --check`).
- [x] Desktop and mobile Playwright checks pass without console errors or horizontal document overflow.
- [x] The five CP8 workflows parse; the release workflow uploads the script and kit only after the gates pass.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (15/15)
