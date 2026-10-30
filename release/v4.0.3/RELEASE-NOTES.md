# Arc Posture Review v4.0.3 - release preparation

Patch release on top of v4.0.2 (`b84d087`).

## Changes

- Evidence availability: a required evidence field is available only when its dataset is a member of the evidence package; a declared source alone no longer counts. Defense in depth: the collector already marks missing datasets as ERROR.
- New negative test `tools/Test-EvidenceAvailability.py` (fails on v4.0.2, passes on v4.0.3).
- Security review addendum `docs/v4/security-review-addendum-v4.0.3.md`: corrects the SHA256SUMS statement of the v4.0.1/v4.0.2 records (v4.0.0 tag blobs 43/43) and records a real-environment validation (lab, 7 Azure Arc machines).

## Unchanged

- Collection, scoring, canonical contract (`assessment-result.v4`, contract 4.0.0) and report rendering. Results are unchanged for packages in which every declared dataset is present.

## Deferred to v4.1.0

- CHK-42/55/57/63 inconclusive-evidence handling and the other v4.0.2 deferrals.
- F2 coverage derived from status; F3 adverse results not gated by missing fields; F4 fixture without `data/*.json`; F5 N/A never NOT_APPLICABLE; F6 checkpoint 4 gate leaves untracked reports.

## Verification

- `python tools/Invoke-V4FinalGates.py --profile release` and `--profile all`.
- `release/v4.0.3/SHA256SUMS`: SHA-256 of LF-normalised content.

Publication remains blocked until the v4.0.3 security review is approved.
