# Arc Posture Review v4.3.6 — sources and test coverage

**Status:** APPROVED_FOR_PUBLICATION — 11/11 checklist items verified by the release gates and recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-06. This is the project's own checklist, not an independent audit. Tagging and publishing remain a separate, manual step.

## Changed

- **Prices:** `PRICES-LIST` is an official source: Defender for Servers Plan 1 USD 5, Plan 2 USD 15, Azure Update Manager USD 5 per server per month, Windows Server pay-as-you-go USD 33.58 per core per month, matching the collector constants. `docs/sources.*.md` regenerated.
- **CVE-2025-26627:** verified against MSRC. It is the Azure Arc Installer vulnerability that affects only machines onboarded with the Group Policy script below 1.0.10; it does not map to a Connected Machine agent version, so it stays out of the per-machine list.

## Preserved

- App, collector logic, results, 64 checks and 11 scenarios, canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
