# Known issues — v4.0.0 release preparation

## KI-V4-001 — pypdf Dependabot alerts

- **Status:** OPEN — STABLE RELEASE BLOCKER
- **Affected approved dependency:** `pypdf==6.19.0`
- **Observed security queue:** 11 Dependabot alerts
- **Desired patch:** `6.21.2`
- **Constraint:** `6.21.2` is unavailable in the approved package feed.
- **Effect:** v4.0.0-rc.1 validation may continue, but stable v4.0.0 publication is blocked.
- **Exit criteria:** the approved feed carries a remediated version and all gates pass with the updated pin, or the security owner records a time-bounded formal acceptance through the organization’s normal process.

No workflow or integration script in this package bypasses this blocker or suppresses the alerts.

## v4.1.0 review notes

Earlier candidates allowed the embedded guide markers to drift from the collector version. v4.1.0 aligns those markers and adds `tools/Test-GuideVersion.py` to the checkpoint 4 gate. This candidate remains non-publishable until independent test and Git provenance validation are completed.
