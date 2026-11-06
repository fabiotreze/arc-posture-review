# Arc Posture Review v4.1.1 — posture versus evidence patch candidate

**Status:** VALIDATED_ARTIFACT — not publishable until Git provenance, independent package testing and the security review record are confirmed.

## Fixed

- A missing configuration or missing evidence is no longer reported as a conclusive FAIL: CHK-23 and CHK-56 are WARN, and CHK-18, CHK-31, CHK-33, CHK-41, CHK-43 and CHK-45 return PARTIAL when the evidence cannot support a conclusion. Explicit adverse evidence (for example NonCompliant, a Free Defender tier or an expired agent) stays FAIL.
- A run without `-Subscriptions` or `-ManagementGroup` now warns that only the default Azure CLI subscription is queried, and CHK-01 returns PARTIAL instead of reporting zero machines with full coverage.
- The collector warns when the same resource group and machine name exist in more than one subscription.
- N/A results carry FULL evidence coverage, so non-applicability is no longer treated as unassessed.
- Scenarios driven only by not-verified controls cannot reach the NOW horizon, and a defense function with only informational or not-applicable controls is UNKNOWN, not EFFECTIVE.
- The v4 report has a report-style executive summary: verified gaps, improvement opportunities and not-verified controls, with check titles, and an action plan grouped by what to do. Action cards carry a `basis`.
- Guide, README, HTML pages and guide-version markers state v4.1.1; the stale "Canonical guide" badge is now checked by `tools/Test-GuideVersion.py`.
- `pypdf` moved to `6.21.4`, closing the 14 open Dependabot alerts.

## Preserved

- 64 checks (`CHK-01..CHK-64`) and 11 scenarios (`AS01..AS11`).
- Canonical `assessment-result.v4` contract version `4.0.0` (optional action-card field `basis` added).
- Collector schema version 3.

## Distribution status

This package is for application and independent testing. It contains no collected environment data or customer reports. Publication remains blocked until authorized Git provenance/push and independent test approval are confirmed.
