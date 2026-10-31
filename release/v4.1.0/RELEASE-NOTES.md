# Arc Posture Review v4.1.0 — evidence hardening test candidate

## Fixed

- CHK-42 rejects missing, duplicate, unsuccessful, malformed, or untimestamped patch-assessment evidence from PASS.
- CHK-55 requires a recognized OS baseline plus timestamped compliance evidence.
- CHK-57 preserves conclusive Defender FAIL/WARN results when MDE extension proxy coverage is incomplete.
- CHK-63 treats unread resource-level Defender plans as PARTIAL rather than PASS or inferred Free.
- The GitHub Actions release step now creates or updates a release idempotently and replaces the collector asset with `--clobber`.

## Preserved

- 64 checks (`CHK-01..CHK-64`).
- 11 scenarios (`AS01..AS11`).
- Canonical `assessment-result.v4` contract version `4.0.0`.
- Collector schema version 3.

## Distribution status

This package is for application and independent testing. It contains no collected environment data or customer reports. Publication remains blocked until authorized Git provenance/push and independent test approval are confirmed.
