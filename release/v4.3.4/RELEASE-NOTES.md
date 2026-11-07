# Arc Posture Review v4.3.4 — sources and test coverage

**Status:** APPROVED_FOR_PUBLICATION — 11/11 checklist items verified by the release gates and recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-06. This is the project's own checklist, not an independent audit. Tagging and publishing remain a separate, manual step.

## Changed

- **Claim register:** `ACTIVITYLOG-90D` (Azure Monitor activity log retention period), `SQL-USAGE-24H` (Manage Licensing and Billing), `ESU-2008` (reworded to what the Update Manager ESU page documents: 2012, 2012 R2 and 2016) and the new `PRICES-GC` (USD 6 per server per month on the Azure Arc pricing page) are official sources. `docs/sources.*.md` regenerated.
- **Open items stated precisely:** the SQL extension threshold 1.1.2859.223 is not a documented minimum (current auto-upgrade target 1.1.3518.465), and the Defender, Update Manager and Windows Server pay-as-you-go prices are not published as numbers on the pages checked. No threshold, price or result changed.

## Preserved

- App, collector logic, results, 64 checks and 11 scenarios, canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
