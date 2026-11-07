# Arc Posture Review v4.3.3 — sources and test coverage

**Status:** APPROVED_FOR_PUBLICATION — 11/11 checklist items verified by the release gates and recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-06. This is the project's own checklist, not an independent audit. Tagging and publishing remain a separate, manual step.

## Changed

- **Claim register:** the SQL Server pay-as-you-go 30-day limit (`SQL-PAYG-30D`) is now an official source (Microsoft Learn, *Manage the transition to pay-as-you-go billing*): machines must check in at least every 30 days.
- **Wording corrected (EN-US and pt-BR; collector, guide, catalog, criteria):** the texts said the PAYG subscription expires and use is no longer authorized after 30 days. The source says that after more than 30 days disconnected the SQL Arc service switches to recurring billing based on the last known configuration, with backfill charges for the previous 30 days, and a changed VM ID can cause double billing. CHK-64 results and thresholds are unchanged; only the explanation changed.

## Preserved

- App, collector logic, results, 64 checks and 11 scenarios, canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
