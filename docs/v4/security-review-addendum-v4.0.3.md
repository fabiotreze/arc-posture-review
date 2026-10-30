# Arc Posture Review v4.0.3 security review addendum

Re-validation performed on 2026-10-30 against v4.0.2 (`b84d087`). Published security review records for v4.0.1 and v4.0.2 are not modified; this addendum corrects and complements them.

## Corrections to published records

- **SHA256SUMS (v4.0.1 and v4.0.2 records).** The statement "3 of 43 entries do not match the v4.0.0 tag blobs" is incorrect. Against the v4.0.0 tag blobs, 43/43 entries match. A Windows checkout with `core.autocrlf=true` diverges for 41/43 text files because of CRLF conversion. Validate against tag blobs (`git show v4.0.0:<path>`) or a checkout with `core.autocrlf=false`.
- **"PARTIAL coverage does not silently become FULL".** The synthetic reviewed-lab fixture reports 24 evidence records with coverage FULL and required fields missing. Root cause: the fixture package carries no `data/*.json` members. Missing fields are disclosed (`MISSING_REQUIRED_EVIDENCE`, `REQUIRED_FIELDS_MISSING`) and no PASS or N/A escapes the evidence gate. A real lab run reports 0 such records.

## Real-environment validation

Lab subscription with 7 Azure Arc machines, collector v4.0.2, read-only. Environment identifiers and the collection package are intentionally not recorded.

- Missing evidence never yields EFFECTIVE: 0 violations (8 EFFECTIVE, all FULL/SUPPORTED/HIGH).
- INEFFECTIVE and AT_RISK are backed by direct or bounded evidence: 0 violations.
- CHK-42 and CHK-57: UNASSESSED (PARTIAL). CHK-55: INEFFECTIVE (FULL/HIGH). CHK-63: EFFECTIVE with per-machine plan read 7/7 and no read errors. The deferred CHK-42/55/57/63 item remains for failure scenarios.
- Release checks: SHA256SUMS v4.0.0 43/43, Dependabot open alerts 0, `pypdf` installed equals pin (6.21.2), PSScriptAnalyzer Error/Warning 0, legacy Playwright/PDF PASS.

## Hardening in v4.0.3

- **F1 Evidence availability from declared sources.** APPLIED. Evidence availability now requires the dataset to be a package member; a declared source alone no longer counts (`assurance/v4/checkpoint4/engine/deterministic_engine.py`). Negative test: `tools/Test-EvidenceAvailability.py`. The collector already marks missing datasets as ERROR (`scripts/Invoke-ArcPostureReview.ps1`), so this is defense in depth.

## Deferred to v4.1.0 (methodology changes)

- **F2** Evidence coverage is derived from result status: 125 `Write-Result` calls, none with explicit coverage; 2 direct PARTIAL assignments. Coverage and outcome are not fully independent axes.
- **F3** FAIL and WARN are not gated by missing required fields in the engine. Not observed in the real run.
- **F4** The fixture package should include `data/*.json` members so the availability path is exercised end to end.
- **F5** The collector sets coverage NONE for N/A while the engine requires FULL for NOT_APPLICABLE, so N/A always becomes UNASSESSED (3 of 3 in the real run). Conservative, but NOT_APPLICABLE is never exercised in real runs.
- **F6** `assurance/v4/checkpoint4/scripts/Invoke-AllGates.py` leaves untracked output in `assurance/v4/checkpoint4/reports/`. The final entrypoint preserves the working tree; per-checkpoint gates do not. Add the reports path to `.gitignore` or write outside the repository.

Reviewer: Fabio Rodrigues Vieira Costa
Date: 2026-10-30

**Decision:** APPROVED
