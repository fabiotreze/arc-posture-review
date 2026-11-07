# Arc Posture Review v4.3.2 — sources and test coverage

**Status:** APPROVED_FOR_PUBLICATION — 11/11 checklist items verified by the release gates and recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-06. This is the project's own checklist, not an independent audit. Tagging and publishing remain a separate, manual step.

## Changed

- **Claim register:** the 45-day Expired timeline (`AGENT-DISCONNECT-45D`) is now an official source: the Azure Arc-enabled servers overview, Agent status section (a machine disconnected for 45 days might become Expired; the credential is valid for up to 90 days and renews every 45 days). The 30 to 44 day warning band is a separate kit criterion (`AGENT-DISCONNECT-30D`). `docs/sources.*.md` regenerated.
- **Tests:** `tools/Test-Keyboard.py` (part of the gate) checks Tab order, Enter and Space, visible focus and the menu highlight while scrolling, in the app and the v4 report (EN-US and pt-BR). `tools/Test-Navigation.py --browser firefox|webkit` repeats the navigation test in other engines. The gate uses Chromium.

## Preserved

- App, collector logic, results, 64 checks and 11 scenarios, canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
