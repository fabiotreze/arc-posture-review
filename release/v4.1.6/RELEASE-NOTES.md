# Arc Posture Review v4.1.6 — fidelity fixes patch candidate

**Status:** APPROVED_FOR_PUBLICATION — security review approved by Fabio Rodrigues Vieira Costa on 2026-11-06 (15/15). Tagging and publishing remain a separate, manual step.

## Fixed

- **CHK-21** no longer labels every open agent port as SSH/Windows Admin Center. It classifies 22 (SSH), 3389 (RDP) and 6516 (Windows Admin Center), reports other ports as unclassified, and says an open port is a posture item, not evidence of exposure.
- **CHK-33** counts distinct Arc machines; nested resources (for example SQL Server objects) no longer inflate the machine count.
- Added `CONTRIBUTING.md`, an issue template and a pull request template (no collected data in issues; vulnerabilities through private reporting).

## Preserved

- 64 checks and 11 scenarios; scores and priorities follow the same rules.
- Canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
