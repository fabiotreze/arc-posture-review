# Known issues — v4.0.0 release preparation

## KI-V4-001 — pypdf Dependabot alerts

- **Status:** RESOLVED — remediated by upgrading the approved pin
- **Previous approved dependency:** `pypdf==6.19.0`
- **Current approved dependency:** `pypdf==6.21.2`
- **Observed security queue before remediation:** 11 Dependabot alerts per requirements file (`requirements-v4.txt` and `requirements-dev.txt`)
- **Remediation:** `6.21.2` is the highest first-patched version among those alerts. It now resolves from the approved package feed, both requirements files carry the new pin and the CP8/CP9/CP10 gates validate the resolved state.
- **Effect:** the dependency blocker is closed. Stable v4.0.0 publication still requires the security-review checklist to be repeated and approved.

No workflow or integration script in this package bypasses the release gates or suppresses alerts.
