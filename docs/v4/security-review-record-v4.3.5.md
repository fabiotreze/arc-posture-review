# Arc Posture Review v4.3.5 — review record

## Scope

- CHK-34 threshold: fixed 1.1.2859.223 replaced by a 12-month release window (kit criterion `SQLEXT-12M`); guide, catalog and criteria wording updated.
- Register: CVE-2025-26627 NVD data and Update Manager pricing model recorded; `docs/sources.*.md` regenerated.
- Version alignment for v4.3.5. No change to the app logic, engine, canonical contract or other checks.

## Validation state

- Decision: see the line at the end. The approval is recorded by the assistant on the reviewer's instruction, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer pass.

## Publication security review

- [x] The collector logic is unchanged and performs no Azure write.
- [x] The kit still equals the pinned SHA-256 (`tools/Build-Kit.py --check`).
- [x] Localization parity holds between EN-US and pt-BR, including the new section subtitles (`Test-LocalizationParity.py`, `Test-PtBrContent.py`).
- [x] PSScriptAnalyzer reports no Error/Warning for the collector and the BOM is intact.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Spelling was reviewed in the English and Portuguese texts (dictionary and LanguageTool passes); British spellings were fixed in live files.
- [x] `tools/Test-Navigation.py` (part of the gate) passes: every wizard step, jump, menu link, filter, saved-analysis anchor and internal Markdown link works in EN-US and pt-BR.
- [x] Release manifest and `SHA256SUMS` validate.
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.3.1 (`tools/Test-GuideVersion.py`).
- [x] No collector, catalog, guide or criteria text changed; only the register and its generated pages.
- [x] The 12-month window uses the same `$SupportCutoff` and release table as the other extension checks; the claim register passes `tools/Test-ClaimRegister.py`.
- [x] The wording of CHK-34 matches the new threshold in the collector, guide, catalog and criteria (EN-US and pt-BR).

**Decision:** APPROVED — 12/12 checklist items verified by the release gates, recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-06. This is the project's own checklist, not an independent audit.
