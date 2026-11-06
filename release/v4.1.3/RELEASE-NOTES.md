# Arc Posture Review v4.1.3 — app redesign patch candidate

**Status:** APPROVED_FOR_PUBLICATION — security review approved by Fabio Rodrigues Vieira Costa on 2026-11-06 (15/15). Tagging and publishing remain a separate, manual step.

## Changed

- The Analysis opens with a **verdict**: verified gaps, improvement opportunities and points not yet verified, a status bar and the three actions to do first.
- The Guide opens on **Start here** (Collect, Open, Deliver) with a search box.
- The collection wizard defaults to the **subscription list**; the current-subscription mode warns that it only queries the `az login` default subscription.
- Refreshed theme for the app and the saved analysis (light and dark, print).

## Preserved

- 64 checks (`CHK-01..CHK-64`) and 11 scenarios (`AS01..AS11`).
- Canonical `assessment-result.v4` contract version `4.0.0` and collector schema version 3.
- Read-only Azure access; the collector logic is unchanged.
- Single package (v4.1.2): the `.zip` carries `report/` and the runtime kit stays pinned by SHA-256.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step; the release workflow re-verifies the manifest and `SHA256SUMS`, rebuilds the kit and uploads it with the script.
