# Arc Posture Review v4.3.8 — sources and test coverage

**Status:** APPROVED_FOR_PUBLICATION — 11/11 checklist items verified by the release gates and recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-07. This is the project's own checklist, not an independent audit. Tagging and publishing remain a separate, manual step.

## Changed

- **CHK-51:** Windows Server 2016 machines whose ESU is assigned and whose agent is 1.62 or later no longer appear as rows or in `found`; only machines with a pending item do. The package verifier follows the same rule. Found by the first real collections.
- **Wording:** the checks, guide, catalog and PT-BR rules say a machine disconnected for 45 days *might* become Expired, as Microsoft Learn states, instead of asserting it. Known-issues pages updated: every register claim is classified. Keyboard navigation confirmed on Safari (macOS) by the maintainer.

## Preserved

- App, collector logic, results, 64 checks and 11 scenarios, canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
