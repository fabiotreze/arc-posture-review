# Known issues — v4.0.1

## KI-V4-001 — pypdf Dependabot alerts

- **Status:** RESOLVED — remediated by upgrading the approved pin
- **Previous approved dependency:** `pypdf==6.19.0`
- **Current approved dependency:** `pypdf==6.21.2`
- **Observed security queue before remediation:** 11 Dependabot alerts per requirements file (`requirements-v4.txt` and `requirements-dev.txt`)
- **Remediation:** `6.21.2` is the highest first-patched version among those alerts. It now resolves from the approved package feed, both requirements files carry the new pin and the CP8/CP9/CP10 gates validate the resolved state.
- **Effect:** the dependency blocker is closed. The v4.0.0 security review was repeated and approved on 2026-10-29 and v4.0.0 is published.

No workflow or integration script in this package bypasses the release gates or suppresses alerts.

## v4.0.3 review notes

See `docs/v4/security-review-addendum-v4.0.3.md`: SHA256SUMS statement correction, fixture-only coverage artefact, evidence availability hardening (F1), and items deferred to v4.1.0 (F2, F3, F4, F5, F6).

## v4.0.4 review notes

CHK-32 and CHK-39 returned PASS against an empty connected-machine target when the Arc inventory had machines but none was Connected (v4.0.3 and earlier). Fixed in v4.0.4: both return N/A; see `docs/v4/security-review-record-v4.0.4.md`.
