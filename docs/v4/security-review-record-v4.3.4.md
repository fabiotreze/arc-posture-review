# Arc Posture Review v4.3.4 — review record

## Scope

- Claim register: four claims sourced from Microsoft pages; `docs/sources.*.md` regenerated.
- Open items (SQL extension threshold, remaining prices) state what is still to be decided; no threshold, price or result changed.
- Version alignment for v4.3.4. No change to the app logic, collector logic, engine or canonical contract.

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
- [x] The claim register passes `tools/Test-ClaimRegister.py`: each official entry carries a Microsoft URL, a quotation and a date.
- [x] No collector, catalog, guide or criteria text changed; only the register and its generated pages.

**Decision:** APPROVED — 11/11 checklist items verified by the release gates, recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-06. This is the project's own checklist, not an independent audit.
