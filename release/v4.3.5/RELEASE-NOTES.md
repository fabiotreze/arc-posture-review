# Arc Posture Review v4.3.5 — sources and test coverage

**Status:** APPROVED_FOR_PUBLICATION — 12/12 checklist items verified by the release gates and recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-06. This is the project's own checklist, not an independent audit. Tagging and publishing remain a separate, manual step.

## Changed

- **CHK-34 (SQL extension):** a SQL Server extension is reported when its release month (from the Microsoft release table) is older than 12 months before the run date, or when automatic upgrade is off. This replaces the fixed 1.1.2859.223 threshold, which the release notes do not document as a minimum. Registered as the kit criterion `SQLEXT-12M`. Guide, catalog and criteria wording updated (EN-US and pt-BR). Results can change: extensions from 2025-10 and earlier that were accepted before are now reported.
- **Register:** `AGENT-CVE-2025-26627` records the NVD data (published 2025-03-11, Azure Arc below 1.0.10; MSRC page unavailable, still unmapped to an agent version). `PRICES-LIST` records the Update Manager pricing model; numeric prices remain unpublished on the pages checked.

## Preserved

- 64 checks and 11 scenarios, canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access, every other threshold and price.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
