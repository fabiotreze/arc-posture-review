# Arc Posture Review v4.3.0 — review record

## Scope

- Visual redesign of the browser app (analysis, guide, wizard) and of the canonical v4 report: one set of design tokens, tinted status colors, numbered sections, one table style, one-line purpose under each v4 report section, dark mode and print/PDF following the same tokens (`docs/v4.3.0-calm-design.md`).
- The app analysis folds the kit-index explanation and the two reading notes, removes the Quick read gain list that repeated "Do first", and fixes a stray `\1` next to the scope selector.
- Sample analyses migrated to the new markup; no collector, engine or canonical change.
- Version alignment for v4.3.0.

## Preserved boundaries

- Collector logic and results are unchanged; 64 checks and 11 scenarios; `assessment-result.v4` contract version `4.0.0`; collector schema version 3.
- The renderer stays render-only: no risk, priority, scenario or roadmap calculation was added (`Test-RenderPurity.py`).
- The workflows keep `contents: read`, the approved action set and no mutating release action.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: see the line at the end. The approval is recorded by the assistant on the reviewer's instruction, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer pass.

## Publication security review

- [x] The collector logic is unchanged and performs no Azure write.
- [x] Only presentation changed (CSS, wrapper markup, section subtitles); `assessment-result.v4.json` passes JSON Schema and semantic validation and CHK-01..CHK-64 occur exactly once.
- [x] Canonical text values still appear in the report (`Test-ReportContract.py`); Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] Every status badge keeps a color rule and carries a text label (`Test-StatusColors.py`); the tints use dark text on pale backgrounds.
- [x] The saved analysis keeps its Content-Security-Policy and the pinned runtime hash; no script was added to the pages.
- [x] The embedded collector, criteria and CSS in the pages match their sources (`tools/Sync-ReportAssets.py --check`).
- [x] The kit still equals the pinned SHA-256 (`tools/Build-Kit.py --check`).
- [x] Localization parity holds between EN-US and pt-BR, including the new section subtitles (`Test-LocalizationParity.py`, `Test-PtBrContent.py`).
- [x] The browser app regression and the PDF matrix pass in EN-US and pt-BR.
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.3.0 (`tools/Test-GuideVersion.py`).
- [x] PSScriptAnalyzer reports no Error/Warning for the collector and the BOM is intact.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (13/13)
