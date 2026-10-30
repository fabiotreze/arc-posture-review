# Arc Posture Review v4.0.1 — release preparation

Patch release on top of v4.0.0 (base `d9ae34f`). Collection behaviour, the 64 checks, statuses, scoring and the `assessment-result.v4` contract (4.0.0) are unchanged.

## Included

- Collector, integrated guides, citation metadata and test markers versioned as v4.0.1.
- The published collector asset now includes the v4 report (on by default; `-NoV4Report` to skip); the v4.0.0 asset did not.
- Version-parametrised release preparation (CP10) and v4 release-gate workflow; `release/v4.0.0` is kept unchanged as the published record.
- The tag-triggered Release workflow refuses v4+ tags without an approved release manifest and a valid `SHA256SUMS`.
- `tools/Prepare-Release.py` regenerates `SHA256SUMS` and records approval only when the security-review record has no unchecked items.
- Stale status text corrected in the methodology and known issues.
- `SHA256SUMS` uses LF-normalised content, so it validates identically on Windows (`core.autocrlf`) and on Linux runners.

## Not included (planned for v4.1.0)

- CHK-42, CHK-55, CHK-57, CHK-63: no PASS on inconclusive evidence (assessment age limit, pending baseline, sensor health, per-machine plan read failures), with negative tests
- CHK-31, CHK-39, CHK-43, CHK-45: separate organisational policy from Microsoft requirement (approved destinations, per-table retention)
- CHK-02: Arc-enabled SCVMM lifecycle instead of a generic recommendation for new projects
- Sources: pin the MCSB version per mapping and replace the deprecated CAF Arc reference
- Report: per-claim scope/denominator, evidence time, direct vs proxy source, missing permissions, pagination limit and rule version; explicit criteria for 'Verified Improvement'; SHA-256 binding of the resource index

## Publication status

**Status:** PENDING_SECURITY_REVIEW — `publishable: false`. Tagging and publishing remain a separate, manual step.
