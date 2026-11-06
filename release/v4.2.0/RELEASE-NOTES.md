# Arc Posture Review v4.2.0 — foundations of the claims

**Status:** APPROVED_FOR_PUBLICATION — security review approved by Fabio Rodrigues Vieira Costa on 2026-11-06 (17/17). Tagging and publishing remain a separate, manual step.

## New

- A **register of sources** states, for every threshold, date and label, whether it is an official source, an official CVE record, a criterion of the kit or still to verify (`docs/sources.en-US.md`, `docs/sources.pt-BR.md`). A test fails when the collector gains an unregistered threshold.
- `tools/Verify-Package.py` recomputes key numbers from the raw data of a package and compares them with the collector result; it works on any package.

## Fixed

- **CHK-21:** only SSH (22) and Windows Admin Center (6516) are named; other ports are unclassified; port 6516 without the AdminCenter extension is reported.
- **CHK-29:** per-machine CVE ranges follow the NVD (below 1.49, 1.56 and 1.61); the automatic upgrade detail counts machines below 1.67 and failed attempts and states that a local block (`automaticupgrade.blocklocally`) takes precedence and is not readable through Azure; agent 1.69 added to the release calendar.
- The kit index is described as inspired by, not equal to, the Defender for Cloud Secure Score.

## Preserved

- 64 checks and 11 scenarios; canonical `assessment-result.v4` contract version `4.0.0`; collector schema version 3; read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
