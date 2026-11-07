# Arc Posture Review v4.3.7 — sources and test coverage

**Status:** APPROVED_FOR_PUBLICATION — 11/11 checklist items verified by the release gates and recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-07. This is the project's own checklist, not an independent audit. Tagging and publishing remain a separate, manual step.

## Changed

- **Verifier (`tools/Verify-Package.py`):** two real collections (one capped with `maxMachines`, one with all machines disconnected) produced four false FAILs. V01 and V21 now use the sample size or the whole-scope total when the run was capped; V22 counts only baselines of connected machines (the collector returns N/A when none is connected); V23 includes Windows Server 2016 rows, which the collector lists with their ESU situation. After the fix both packages report 0 disagreements.
- **Test:** `tools/Test-VerifyPackage.py` has a case with the three shapes; it fails on the previous verifier and passes now.

## Preserved

- App, collector logic, results, 64 checks and 11 scenarios, canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
